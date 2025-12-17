from Rider_Dashboard.rider_db import RiderDB


class RiderService:
    def __init__(self, username):
        self.db = RiderDB()
        self.driver_id, self.driver_email, self.driver_name = self.db.resolve_driver(username)

    def get_stats(self):
        """Get driver statistics."""
        return self.db.get_driver_stats(self.driver_id)

    def get_trips(self):
        """Get all trips for the driver."""
        return self.db.get_driver_trips(self.driver_id)

    def accept_ride(self, booking_id):
        """Accept a ride."""
        status = self.db.get_booking_status(booking_id)
        if status in ("Cancelled", "Completed", "Accepted"):
            raise ValueError(f"Cannot accept booking with status '{status}'")
        self.db.accept_ride(booking_id, self.driver_id)

    def complete_ride(self, booking_id):
        """Complete a ride and update ride completion timestamp.
        
        Args:
            booking_id (int): The ID of the booking to complete
            
        Raises:
            ValueError: If the booking is not in 'Accepted' status
            Exception: If there's an error completing the ride
        """
        # Get current booking status
        status = self.db.get_booking_status(booking_id)
        
        # Validate booking can be completed
        if status != "Accepted":
            raise ValueError(
                f"Only 'Accepted' bookings can be completed. "
                f"Current status: '{status}'"
            )
            
        try:
            # Complete the ride and update timestamps
            self.db.complete_ride(booking_id, self.driver_id)
            
            # Log the completion
            print(f"Ride {booking_id} completed by driver {self.driver_id}")
            
        except Exception as e:
            print(f"Error completing ride {booking_id}: {str(e)}")
            raise

    def get_profile(self):
        """Get driver profile."""
        return self.db.get_driver_profile(self.driver_id)

    def update_profile(self, name, phone, address):
        """Update driver profile."""
        if not name or not phone or not address:
            raise ValueError("Name, Phone and Address are required")
        self.db.update_driver_profile(self.driver_id, name, phone, address)

    def update_photo_path(self, photo_path):
        """Update driver photo path."""
        self.db.update_driver_photo_path(self.driver_id, photo_path)

