from datetime import datetime
from Admin_Dashboard.admin_db import AdminDB


class AdminService:
    def __init__(self, admin_id):
        self.db = AdminDB()
        self.admin_id = self.db.resolve_admin_id(admin_id)

    def get_stats(self):
        """Get dashboard statistics."""
        return self.db.get_stats()

    def get_all_bookings(self):
        """Get all bookings."""
        return self.db.get_all_bookings()

    def cancel_booking(self, booking_id):
        """Cancel a booking."""
        self.db.cancel_booking(booking_id)

    def get_drivers_for_assignment(self):
        """Get drivers for assignment dropdown."""
        return self.db.get_drivers_for_assignment()

    def get_booking(self, booking_id):
        """Get a booking by ID."""
        return self.db.get_booking(booking_id)

    def assign_driver(self, booking_id, driver_source, driver_ident):
        """
        Assign a driver to a booking.
        driver_source: 'drivers' or 'users'
        driver_ident: DID or user_id
        """
        # Get booking details
        booking = self.db.get_booking(booking_id)
        if not booking:
            raise ValueError("Booking not found")
        
        bstatus = booking[3] if len(booking) > 3 else None
        if bstatus in ("Cancelled", "Completed"):
            raise ValueError(f"Cannot assign driver to booking with status '{bstatus}'")
        
        bdate = booking[1]
        btime = booking[2]
        
        # Resolve driver ID
        if driver_source == "drivers":
            driver_id = int(driver_ident)
        else:
            driver_id = self.db.ensure_driver_record_for_user(int(driver_ident))
        
        # Check for conflicts
        conflict, conflicting = self.db.check_driver_conflict(driver_id, bdate, btime, ignore_booking_id=booking_id)
        if conflict:
            raise ValueError(
                f"Driver has overlapping booking {conflicting.get('id')} on {conflicting.get('date')} {conflicting.get('time')}."
            )
        
        # Assign driver
        self.db.assign_driver_to_booking(booking_id, driver_id)

    def get_all_users(self):
        """Get all users."""
        return self.db.get_all_users()

    def get_user(self, user_id):
        """Get a user by ID."""
        return self.db.get_user(user_id)

    def update_user(self, user_id, name, phone, address, role):
        """Update user information."""
        if not name or not phone:
            raise ValueError("Name and Phone required")
        self.db.update_user(user_id, name, phone, address, role)

    def delete_user(self, user_id):
        """Delete a user."""
        self.db.delete_user(user_id)

    def get_customers_for_booking(self):
        """Get customers for booking creation."""
        return self.db.get_customers_for_booking()

    def create_booking(self, customer_id, pickup, dropoff, date_str, time_str, taxi_type=None):
        """Create a booking."""
        if not pickup or not dropoff or not date_str or not time_str:
            raise ValueError("Please fill required fields")
        
        
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            if dt.date() < datetime.now().date():
                raise ValueError("Cannot create booking for past date")
            elif dt < datetime.now():
                raise ValueError("Cannot create booking for past time")
            
        except ValueError as e:
            if "Cannot create booking" in str(e):
                raise
            raise ValueError("Invalid date/time format")
        
        self.db.create_booking(customer_id, pickup, dropoff, date_str, time_str, taxi_type)

    def create_or_update_driver(self, name, email, phone, lic, reg, pwd):
        """Create or update a driver."""
        if not name or not email or not phone:
            raise ValueError("Name, Email and Phone required")
        self.db.create_or_update_driver(name, email, phone, lic, reg, pwd)

    def get_profile(self):
        """Get admin profile."""
        return self.db.get_admin_profile(self.admin_id)

    def update_profile(self, name, phone, address):
        """Update admin profile."""
        if not name or not phone or not address:
            raise ValueError("Name, Phone and Address are required")
        self.db.update_admin_profile(self.admin_id, name, phone, address)

    def update_photo_path(self, photo_path):
        """Update admin photo path."""
        self.db.update_admin_photo_path(self.admin_id, photo_path)

