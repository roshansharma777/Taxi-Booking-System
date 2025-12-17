from db import create_connection
from datetime import datetime, timedelta
#from constants import BookingStatus, DriverStatus


class AdminDB:
    def resolve_admin_id(self, ident):
        """Resolve admin identifier to user ID."""
        if ident is None:
            raise ValueError("No admin identifier provided.")

        try:
            if isinstance(ident, int):
                return ident
            if isinstance(ident, str) and ident.isdigit():
                return int(ident)
        except Exception:
            pass

        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed while resolving admin id.")
        cur = None
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM users WHERE (full_name=%s OR email=%s OR phone=%s) AND role='Admin' LIMIT 1",
                (ident, ident, ident)
            )
            row = cur.fetchone()
            if not row:
                raise LookupError(f"No admin found for identifier '{ident}'")
            return int(row[0])
        finally:
            try:
                if cur:
                    cur.close()
            except:
                pass
            try:
                conn.close()
            except:
                pass

    def get_stats(self):
        """Get dashboard statistics."""
        conn = create_connection()
        if not conn:
            return {"customers": 0, "drivers": 0, "bookings": 0}
        
        cur = conn.cursor()
        try:
            try:
                cur.execute("SELECT COUNT(*) FROM users WHERE role='Customer'")
                total_customers = cur.fetchone()[0]
            except Exception:
                total_customers = 0
            
            try:
                cur.execute("SELECT COUNT(*) FROM drivers")
                total_drivers = cur.fetchone()[0]
            except Exception:
                total_drivers = 0
            
            try:
                cur.execute("SELECT COUNT(*) FROM bookings")
                total_bookings = cur.fetchone()[0]
            except Exception:
                total_bookings = 0
            
            return {
                "customers": total_customers,
                "drivers": total_drivers,
                "bookings": total_bookings
            }
        finally:
            cur.close()
            conn.close()

    def get_all_bookings(self):
        """Get all bookings with customer and driver info."""
        conn = create_connection()
        if not conn:
            return []
        
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT b.id, b.user_id, b.pickup, b.dropoff, b.date, b.time, b.status, b.driver_id, "
                "b.ride_start_timestamp, b.ride_completion_timestamp "
                "FROM bookings b ORDER BY b.id DESC"
            )
            bookings = cur.fetchall() or []
            
            user_ids = {b[1] for b in bookings if len(b) > 1 and b[1] is not None}
            driver_ids = {b[7] for b in bookings if len(b) > 7 and b[7] is not None}
            
            user_map = {}
            if user_ids:
                cur.execute(
                    "SELECT id, full_name, email FROM users WHERE id IN (%s)"
                    % ",".join(str(int(x)) for x in user_ids)
                )
                for r in cur.fetchall() or []:
                    user_map[r[0]] = {"name": r[1], "email": r[2]}
            
            driver_map = {}
            if driver_ids:
                cur.execute(
                    "SELECT DID, Name FROM drivers WHERE DID IN (%s)"
                    % ",".join(str(int(x)) for x in driver_ids)
                )
                for r in cur.fetchall() or []:
                    driver_map[r[0]] = r[1]
            
            result = []
            for b in bookings:
                bid = b[0]
                uid = b[1]
                pickup = b[2] if len(b) > 2 else ""
                dropoff = b[3] if len(b) > 3 else ""
                date = b[4] if len(b) > 4 else ""
                time = b[5] if len(b) > 5 else ""
                status = b[6] if len(b) > 6 else ""
                did = b[7] if len(b) > 7 else None
                ride_start = b[8] if len(b) > 8 else None
                ride_completion = b[9] if len(b) > 9 else None
                
                cust_name = user_map.get(uid, {}).get("name") if uid else ""
                driver_name = driver_map.get(did) if did else ""
                cust_display = cust_name if cust_name else (str(uid) if uid else "")
                
                result.append({
                    "id": bid,
                    "customer": cust_display,
                    "pickup": pickup,
                    "dropoff": dropoff,
                    "date": date,
                    "time": time,
                    "status": status,
                    "driver": driver_name,
                    "ride_start_timestamp": ride_start,
                    "ride_completion_timestamp": ride_completion
                })
            
            return result
        finally:
            cur.close()
            conn.close()

    def cancel_booking(self, booking_id):
        """Cancel a booking."""
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")
        
        cur = conn.cursor()
        try:
            cur.execute("UPDATE bookings SET status=%s WHERE id=%s", ("Cancelled", booking_id))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def get_drivers_for_assignment(self):
        """Get all drivers for assignment dropdown."""
        conn = create_connection()
        if not conn:
            return []
        
        cur = conn.cursor()
        try:
            drivers_rows = []
            try:
                cur.execute("SELECT DID, Name, Email, driver_status FROM drivers ORDER BY Name")
                drivers_rows = cur.fetchall() or []
            except Exception:
                pass
            
            user_drivers = []
            try:
                cur.execute("SELECT id, full_name, email FROM users WHERE role='Driver' ORDER BY full_name")
                user_drivers = cur.fetchall() or []
            except Exception:
                pass
            
            options = []
            value_map = {}
            
            for d in drivers_rows:
                did = d[0]
                name = d[1] if len(d) > 1 else ""
                email = d[2] if len(d) > 2 else ""
                status = d[3] if len(d) > 3 else ""
                # Normalize status display: Active/Inactive
                status_display = "Active" if status and status.lower() in ("active", "available") else "Inactive"
                # Use color coding in label for clarity
                status_indicator = "🟢" if status_display == "Active" else "🔴"
                label = f"{status_indicator} {did} - {name} ({email}) [{status_display}]"
                options.append(label)
                value_map[label] = ("drivers", did)
            
            existing_driver_emails = {d[2].lower() for d in drivers_rows if len(d) > 2 and d[2]}
            for u in user_drivers:
                uid = u[0]
                uname = u[1] if len(u) > 1 else ""
                uemail = u[2] if len(u) > 2 else ""
                if uemail and uemail.lower() in existing_driver_emails:
                    continue
                label = f"🟡 U{uid} - {uname} ({uemail}) [user-only]"
                options.append(label)
                value_map[label] = ("users", uid)
            
            return options, value_map
        finally:
            cur.close()
            conn.close()

    def get_booking(self, booking_id):
        """Get a single booking by ID."""
        conn = create_connection()
        if not conn:
            return None
        
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, date, time, status FROM bookings WHERE id=%s LIMIT 1", (booking_id,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def ensure_driver_record_for_user(self, user_id):
        """Ensure a driver record exists for a user, create if needed."""
        conn = create_connection()
        if not conn:
            raise RuntimeError("DB connection failed")
        
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, full_name, email, phone, address FROM users WHERE id=%s LIMIT 1", (user_id,))
            u = cur.fetchone()
            if not u:
                raise LookupError("User not found")
            
            uid = u[0]
            uname = u[1] if len(u) > 1 else ""
            uemail = u[2] if len(u) > 2 else None
            uphone = u[3] if len(u) > 3 else None
            uaddr = u[4] if len(u) > 4 else None
            
            if uemail:
                cur.execute("SELECT DID FROM drivers WHERE Email=%s LIMIT 1", (uemail,))
                r = cur.fetchone()
                if r:
                    return int(r[0])
            
            cur.execute(
                "INSERT INTO drivers (Name, Email, Phone, Address, License_num, Registration_num, Password, driver_status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (uname, uemail, uphone, uaddr, "", "", "", "Active")
            )
            conn.commit()
            cur.execute("SELECT LAST_INSERT_ID()")
            new_did = cur.fetchone()[0]
            cur.execute("UPDATE users SET role=%s WHERE id=%s", ("Driver", uid))
            conn.commit()
            return int(new_did)
        finally:
            cur.close()
            conn.close()

    def assign_driver_to_booking(self, booking_id, driver_id):
        """Assign a driver to a booking."""
        from datetime import datetime
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")
        
        cur = conn.cursor()
        try:
            # Set ride start timestamp when driver is assigned
            ride_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("UPDATE bookings SET driver_id=%s, status=%s, ride_start_timestamp=%s WHERE id=%s",
                       (driver_id, "Assigned", ride_start_time, booking_id))
            cur.execute("UPDATE drivers SET driver_status=%s WHERE DID=%s", ("Inactive", driver_id))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def check_driver_conflict(self, driver_id, date_str, time_str, ignore_booking_id=None):
        """Check if driver has a conflicting booking."""
        try:
            slot_start = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except Exception:
            try:
                slot_start = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
            except Exception:
                return False, None
        
        slot_end = slot_start + timedelta(hours=1)
        
        conn = create_connection()
        if not conn:
            return False, None
        
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, date, time, status FROM bookings WHERE driver_id=%s", (driver_id,))
            rows = cur.fetchall() or []
            for r in rows:
                bid = r[0]
                bdate = r[1]
                btime = r[2]
                bstatus = r[3] if len(r) > 3 else None
                if ignore_booking_id and bid == ignore_booking_id:
                    continue
                if bstatus in ("Cancelled", "Completed"):
                    continue
                try:
                    b_start = datetime.strptime(f"{bdate} {btime}", "%Y-%m-%d %H:%M")
                except Exception:
                    try:
                        b_start = datetime.strptime(f"{bdate} {btime}", "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        continue
                b_end = b_start + timedelta(hours=1)
                if (slot_start < b_end) and (b_start < slot_end):
                    return True, {"id": bid, "date": bdate, "time": btime, "status": bstatus}
            return False, None
        except Exception:
            return False, None
        finally:
            cur.close()
            conn.close()

    def get_all_users(self):
        """Get all users."""
        conn = create_connection()
        if not conn:
            return []
        
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, full_name, email, phone, address, role FROM users ORDER BY id DESC")
            return cur.fetchall() or []
        finally:
            cur.close()
            conn.close()

    def get_user(self, user_id):
        """Get a single user by ID."""
        conn = create_connection()
        if not conn:
            return None
        
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, full_name, email, phone, address, role FROM users WHERE id=%s LIMIT 1",
                       (user_id,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def update_user(self, user_id, name, phone, address, role):
        """Update user information."""
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")
        
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE users SET full_name=%s, phone=%s, address=%s, role=%s WHERE id=%s",
                (name, phone, address, role, user_id)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def delete_user(self, user_id):
        """Delete a user."""
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")
        
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def get_customers_for_booking(self):
        """Get all customers for booking creation."""
        conn = create_connection()
        if not conn:
            return []
        
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, full_name, email FROM users WHERE role='Customer' ORDER BY full_name")
            return cur.fetchall() or []
        finally:
            cur.close()
            conn.close()

    def get_addresses(self):
        """Get all addresses for booking creation."""
        conn = create_connection()
        if not conn:
            return []
        
        cur = conn.cursor()
        try:
            cur.execute("SELECT name FROM addresses ORDER BY name")
            return [row[0] for row in cur.fetchall()]
        except Exception:
            return []
        finally:
            cur.close()
            conn.close()

    def create_booking(self, user_id, pickup, dropoff, date, time, taxi_type=None):
        """Create a new booking."""
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")
        
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO bookings (user_id, pickup, dropoff, date, time, taxi_type, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (user_id, pickup, dropoff, date, time, taxi_type, "Booked")
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def create_or_update_driver(self, name, email, phone, lic, reg, pwd):
        """Create or update a driver."""
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")
        
        cur = conn.cursor()
        try:
            cur.execute("SELECT id FROM users WHERE email=%s LIMIT 1", (email,))
            existing = cur.fetchone()
            if existing:
                uid = existing[0]
                cur.execute("UPDATE users SET full_name=%s, phone=%s, role=%s WHERE id=%s",
                           (name, phone, "Driver", uid))
            else:
                cur.execute(
                    "INSERT INTO users (full_name, email, phone, address, gender, role, password, account_created) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (name, email, phone, "", None, "Driver", pwd,
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                cur.execute("SELECT LAST_INSERT_ID()")
                uid = cur.fetchone()[0]
            
            cur.execute("SELECT DID FROM drivers WHERE Email=%s LIMIT 1", (email,))
            drow = cur.fetchone()
            if drow:
                did = drow[0]
                cur.execute(
                    "UPDATE drivers SET Name=%s, Phone=%s, License_num=%s, Registration_num=%s WHERE DID=%s",
                    (name, phone, lic, reg, did)
                )
            else:
                cur.execute(
                    "INSERT INTO drivers (Name, Email, Phone, Address, License_num, Registration_num, Password, driver_status) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (name, email, phone, "", lic, reg, pwd, "Active")
                )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def get_admin_profile(self, admin_id):
        """Get admin profile from users table."""
        conn = create_connection()
        if not conn:
            return None

        cur = conn.cursor()
        try:
            try:
                cur.execute(
                    "SELECT full_name, email, phone, address, gender, role, photo_path "
                    "FROM users WHERE id=%s AND role='Admin' LIMIT 1",
                    (admin_id,)
                )
            except Exception:
                # backward compatibility if photo_path column doesn't exist yet
                cur.execute(
                    "SELECT full_name, email, phone, address, gender, role "
                    "FROM users WHERE id=%s AND role='Admin' LIMIT 1",
                    (admin_id,)
                )
            row = cur.fetchone()
            if row and len(row) == 6:
                # Add None for photo_path if not present
                return row + (None,)
            return row
        finally:
            cur.close()
            conn.close()

    def update_admin_profile(self, admin_id, name, phone, address):
        """Update admin profile."""
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")

        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE users SET full_name=%s, phone=%s, address=%s WHERE id=%s AND role='Admin'",
                (name, phone, address, admin_id)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def update_admin_photo_path(self, admin_id, photo_path):
        """Update admin photo path."""
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")

        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE users SET photo_path=%s WHERE id=%s AND role='Admin'",
                (photo_path, admin_id)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

