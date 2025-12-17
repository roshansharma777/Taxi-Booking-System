from datetime import datetime
from Customer_Dashboard.customer_db import CustomerDB


class CustomerService:
    def __init__(self, customer_identifier):
        self.db = CustomerDB()
        self.customer_id = self.db.resolve_customer_id(customer_identifier)

    def get_basic_info(self):
        return self.db.get_basic_info(self.customer_id)

    def get_profile(self):
        return self.db.get_profile(self.customer_id)

    def update_profile(self, name, phone, address):
        self.db.update_profile(self.customer_id, name, phone, address)

    def create_booking(self, pickup, dropoff, date, time):
        if date < datetime.now().date():
            raise ValueError("Cannot book past date")
        self.db.ensure_bookings_table()
        self.db.insert_booking(self.customer_id, pickup, dropoff, date, time)

    def get_bookings(self):
        self.db.ensure_bookings_table()
        return self.db.get_bookings(self.customer_id)

    def cancel_booking(self, booking_id):
        self.db.cancel_booking(booking_id)

    def get_addresses(self):
        return self.db.get_addresses()

    def update_photo_path(self, photo_path):
        self.db.update_photo_path(self.customer_id, photo_path)