import mysql.connector

def update_database():
    try:
        # Connect to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="CPNnabin@2004dhakal",
            database="taxi_booking_system_test"
        )
        cursor = conn.cursor()
        
        print("Connected to database successfully!")
        
        # Add driver_id column to bookings table if it doesn't exist
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'taxi_booking_system_test' 
            AND TABLE_NAME = 'bookings' 
            AND COLUMN_NAME = 'driver_id'
        """)
        
        if not cursor.fetchone():
            print("Adding driver_id column to bookings table...")
            cursor.execute("""
                ALTER TABLE bookings 
                ADD COLUMN driver_id INT NULL,
                ADD FOREIGN KEY (driver_id) REFERENCES drivers(DID)
                ON DELETE SET NULL
            """)
            print("Successfully added driver_id column to bookings table.")
        else:
            print("driver_id column already exists in bookings table.")
            # 2. Add photo_path column to users table
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'taxi_booking_system_test' 
            AND TABLE_NAME = 'users' 
            AND COLUMN_NAME = 'photo_path'
        """)
        
        if not cursor.fetchone():
            print("Adding photo_path column to users table...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN photo_path VARCHAR(255) NULL
            """)
            print("✅ Successfully added photo_path column to users.")
        else:
            print("✅ photo_path column already exists in users.")
        
        # 3. Add photo_path column to drivers table
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'taxi_booking_system_test' 
            AND TABLE_NAME = 'drivers' 
            AND COLUMN_NAME = 'photo_path'
        """)
        
        if not cursor.fetchone():
            print("Adding photo_path column to drivers table...")
            cursor.execute("""
                ALTER TABLE drivers 
                ADD COLUMN photo_path VARCHAR(255) NULL
            """)
            print("✅ Successfully added photo_path column to drivers.")
        else:
            print("✅ photo_path column already exists in drivers.")
        
        # 4. Add taxi_type column to bookings table
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'taxi_booking_system_test' 
            AND TABLE_NAME = 'bookings' 
            AND COLUMN_NAME = 'taxi_type'
        """)
        
        if not cursor.fetchone():
            print("Adding taxi_type column to bookings table...")
            cursor.execute("""
                ALTER TABLE bookings 
                ADD COLUMN taxi_type VARCHAR(50) NULL
            """)
            print("✅ Successfully added taxi_type column.")
        else:
            print("✅ taxi_type column already exists.")
        
        # 5. Add ride_start_timestamp column to bookings table
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'taxi_booking_system_test' 
            AND TABLE_NAME = 'bookings' 
            AND COLUMN_NAME = 'ride_start_timestamp'
        """)
        
        if not cursor.fetchone():
            print("Adding ride_start_timestamp column to bookings table...")
            cursor.execute("""
                ALTER TABLE bookings 
                ADD COLUMN ride_start_timestamp TIMESTAMP NULL
            """)
            print("✅ Successfully added ride_start_timestamp column.")
        else:
            print("✅ ride_start_timestamp column already exists.")
        
        # 6. Add ride_completion_timestamp column to bookings table
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'taxi_booking_system_test' 
            AND TABLE_NAME = 'bookings' 
            AND COLUMN_NAME = 'ride_completion_timestamp'
        """)
        
        if not cursor.fetchone():
            print("Adding ride_completion_timestamp column to bookings table...")
            cursor.execute("""
                ALTER TABLE bookings 
                ADD COLUMN ride_completion_timestamp TIMESTAMP NULL
            """)
            print("✅ Successfully added ride_completion_timestamp column.")
        else:
            print("✅ ride_completion_timestamp column already exists.")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("\n✅ Database update completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    update_database()
    input("Press Enter to exit...")
        
        