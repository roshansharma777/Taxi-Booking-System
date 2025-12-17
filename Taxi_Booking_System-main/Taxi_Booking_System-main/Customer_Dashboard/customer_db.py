from db import create_connection


class CustomerDB:

    def resolve_customer_id(self, ident):
        if isinstance(ident, int):
            return ident

        if isinstance(ident, str) and ident.isdigit():
            return int(ident)

        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")

        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id FROM users WHERE full_name=%s OR email=%s OR phone=%s LIMIT 1",
                (ident, ident, ident)
            )
            row = cur.fetchone()
        finally:
            cur.close()
            conn.close()

        if not row:
            raise ValueError("Customer not found")

        return int(row[0])

    def get_basic_info(self, user_id):
        conn = create_connection()
        if not conn:
            return None

        cur = conn.cursor()
        try:
            try:
                cur.execute(
                    "SELECT full_name, photo_path FROM users WHERE id=%s",
                    (user_id,)
                )
            except Exception:
                # backward compatibility if column doesn't exist yet
                cur.execute(
                    "SELECT full_name FROM users WHERE id=%s",
                    (user_id,)
                )
            row = cur.fetchone()
            if row and len(row) == 1:
                return (row[0], None)
            return row
        finally:
            cur.close()
            conn.close()

    def get_profile(self, user_id):
        conn = create_connection()
        if not conn:
            return None

        cur = conn.cursor()
        try:
            try:
                cur.execute("""
                    SELECT full_name, email, phone, address, gender, role, photo_path
                    FROM users WHERE id=%s
                """, (user_id,))
            except Exception:
                # backward compatibility if photo_path column doesn't exist yet
                cur.execute("""
                    SELECT full_name, email, phone, address, gender, role
                    FROM users WHERE id=%s
                """, (user_id,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def update_profile(self, user_id, name, phone, address):
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")

        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE users
                SET full_name=%s, phone=%s, address=%s
                WHERE id=%s
            """, (name, phone, address, user_id))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def ensure_bookings_table(self):
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")

        cur = conn.cursor()
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    pickup VARCHAR(255),
                    dropoff VARCHAR(255),
                    date DATE,
                    time VARCHAR(10),
                    status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def insert_booking(self, user_id, pickup, dropoff, date, time):
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")

        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO bookings (user_id, pickup, dropoff, date, time, status)
                VALUES (%s, %s, %s, %s, %s, 'Booked')
            """, (user_id, pickup, dropoff, date, time))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def get_bookings(self, user_id):
        conn = create_connection()
        if not conn:
            return []

        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, pickup, dropoff, date, time, status, 
                       ride_start_timestamp, ride_completion_timestamp
                FROM bookings
                WHERE user_id=%s
                ORDER BY id DESC
            """, (user_id,))
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    def cancel_booking(self, booking_id):
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")

        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE bookings SET status='Cancelled' WHERE id=%s",
                (booking_id,)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def get_addresses(self):
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

    def update_photo_path(self, user_id, photo_path):
        conn = create_connection()
        if not conn:
            raise ConnectionError("Database connection failed")

        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE users SET photo_path=%s WHERE id=%s",
                (photo_path, user_id)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()