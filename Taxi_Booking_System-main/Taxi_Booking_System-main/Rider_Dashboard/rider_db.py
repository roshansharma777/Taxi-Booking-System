from db import create_connection


class RiderDB:
    def resolve_driver(self, ident):
        """
        Resolve driver identifier to driver row.
        Returns: (driver_id, driver_email, driver_name) or raises LookupError
        """
        # Case 1: numeric -> DID directly
        if isinstance(ident, int) or (isinstance(ident, str) and ident.isdigit()):
            did = int(ident)
            conn = create_connection()
            if not conn:
                raise RuntimeError("DB connection failed")
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT DID, Email, Name FROM drivers WHERE DID=%s LIMIT 1",
                    (did,)
                )
                row = cur.fetchone()
            finally:
                cur.close()
                conn.close()

            if not row:
                raise LookupError(f"No driver with DID {did}")
            return int(row[0]), row[1], row[2]

        # Case 2: resolve through users (preferred, since login is from users)
        conn = create_connection()
        if not conn:
            raise RuntimeError("DB connection failed")
        cur = conn.cursor()
        user_email = None
        try:
            cur.execute(
                "SELECT id, full_name, email, phone "
                "FROM users "
                "WHERE email=%s OR phone=%s OR full_name=%s "
                "LIMIT 1",
                (ident, ident, ident)
            )
            urow = cur.fetchone()
            if urow:
                user_email = urow[2]  # email
        finally:
            cur.close()
            conn.close()

        if user_email:
            # now find driver by drivers.Email
            conn2 = create_connection()
            if not conn2:
                raise RuntimeError("DB connection failed")
            cur2 = conn2.cursor()
            try:
                cur2.execute(
                    "SELECT DID, Email, Name "
                    "FROM drivers "
                    "WHERE Email=%s LIMIT 1",
                    (user_email,)
                )
                drow = cur2.fetchone()
            finally:
                cur2.close()
                conn2.close()

            if drow:
                return int(drow[0]), drow[1], drow[2]

        # Case 3: direct search in drivers by Email/Name/Phone
        conn3 = create_connection()
        if not conn3:
            raise RuntimeError("DB connection failed")
        cur3 = conn3.cursor()
        try:
            cur3.execute(
                "SELECT DID, Email, Name FROM drivers "
                "WHERE Email=%s OR Name=%s OR Phone=%s LIMIT 1",
                (ident, ident, ident)
            )
            row = cur3.fetchone()
        finally:
            cur3.close()
            conn3.close()

        if not row:
            raise LookupError(f"No driver found for identifier '{ident}'")

        return int(row[0]), row[1], row[2]

    def get_driver_stats(self, driver_id):
        """Get driver statistics."""
        conn = create_connection()
        if not conn:
            return {"assigned": 0, "active": 0, "completed": 0}

        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT COUNT(*) FROM bookings WHERE driver_id=%s",
                (driver_id,)
            )
            total_assigned = cur.fetchone()[0]

            cur.execute(
                "SELECT COUNT(*) FROM bookings WHERE driver_id=%s AND status='Accepted'",
                (driver_id,)
            )
            total_active = cur.fetchone()[0]

            cur.execute(
                "SELECT COUNT(*) FROM bookings WHERE driver_id=%s AND status='Completed'",
                (driver_id,)
            )
            total_completed = cur.fetchone()[0]

            return {
                "assigned": total_assigned,
                "active": total_active,
                "completed": total_completed
            }
        finally:
            cur.close()
            conn.close()

    def get_driver_trips(self, driver_id):
        """Get all trips for a driver."""
        conn = create_connection()
        if not conn:
            return []

        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT b.id, u.email, b.pickup, b.dropoff, b.date, b.time, b.status, "
                "b.ride_start_timestamp, b.ride_completion_timestamp "
                "FROM bookings b LEFT JOIN users u ON b.user_id = u.id "
                "WHERE b.driver_id=%s ORDER BY b.id DESC",
                (driver_id,)
            )
            rows = cur.fetchall() or []
            result = []
            for r in rows:
                result.append({
                    "id": r[0],
                    "customer_email": r[1] or "",
                    "pickup": r[2] or "",
                    "dropoff": r[3] or "",
                    "date": r[4] or "",
                    "time": r[5] or "",
                    "status": r[6] or "",
                    "ride_start_timestamp": r[7] if len(r) > 7 else None,
                    "ride_completion_timestamp": r[8] if len(r) > 8 else None
                })
            return result
        finally:
            cur.close()
            conn.close()

    def get_booking_status(self, booking_id):
        """Get booking status."""
        conn = create_connection()
        if not conn:
            return None

        cur = conn.cursor()
        try:
            cur.execute("SELECT status FROM bookings WHERE id=%s LIMIT 1", (booking_id,))
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            cur.close()
            conn.close()

    def accept_ride(self, booking_id, driver_id):
        """Accept a ride."""
        from datetime import datetime
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")

        cur = conn.cursor()
        try:
            # Set ride start timestamp when ride is accepted
            ride_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                "UPDATE bookings SET status=%s, driver_id=%s, ride_start_timestamp=%s WHERE id=%s",
                ("Accepted", driver_id, ride_start_time, booking_id)
            )
            cur.execute(
                "UPDATE drivers SET driver_status=%s WHERE DID=%s",
                ("Inactive", driver_id)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def complete_ride(self, booking_id, driver_id):
        """Complete a ride."""
        from datetime import datetime
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")

        cur = conn.cursor()
        try:
            # Set ride completion timestamp when ride is completed
            ride_completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                "UPDATE bookings SET status=%s, ride_completion_timestamp=%s WHERE id=%s",
                ("Completed", ride_completion_time, booking_id)
            )
            # Set rider status to Available (Active) when ride is completed
            cur.execute(
                "UPDATE drivers SET driver_status=%s WHERE DID=%s",
                ("Active", driver_id)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def get_driver_profile(self, driver_id):
        """Get driver profile information."""
        conn = create_connection()
        if not conn:
            return None

        cur = conn.cursor()
        try:
            try:
                cur.execute(
                    "SELECT Name, Email, Phone, Address, driver_status, photo_path "
                    "FROM drivers WHERE DID=%s",
                    (driver_id,)
                )
            except Exception:
                # backward compatibility if photo_path column doesn't exist yet
                cur.execute(
                    "SELECT Name, Email, Phone, Address, driver_status "
                    "FROM drivers WHERE DID=%s",
                    (driver_id,)
                )
            row = cur.fetchone()
            if row and len(row) == 5:
                # Add None for photo_path if not present
                return row + (None,)
            return row
        finally:
            cur.close()
            conn.close()

    def update_driver_profile(self, driver_id, name, phone, address):
        """Update driver profile."""
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")

        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE drivers SET Name=%s, Phone=%s, Address=%s WHERE DID=%s",
                (name, phone, address, driver_id)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def update_driver_photo_path(self, driver_id, photo_path):
        """Update driver photo path."""
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")

        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE drivers SET photo_path=%s WHERE DID=%s",
                (photo_path, driver_id)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

