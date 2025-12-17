from tkinter import *
from login_page import LoginPage
from registration_page import RegistrationPage
from tkinter import messagebox
import mysql.connector
from db import create_connection

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
        
        # Add driver_id column to bookings table if it doesn't exist
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'taxi_booking_system_test' 
            AND TABLE_NAME = 'bookings' 
            AND COLUMN_NAME = 'driver_id'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE bookings 
                ADD COLUMN driver_id INT NULL,
                ADD FOREIGN KEY (driver_id) REFERENCES drivers(DID)
                ON DELETE SET NULL
            """)
            conn.commit()
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
            conn.close()
        return False

# Import dashboards from respective folders
from Admin_Dashboard.admin_ui import AdminDashboard
from Customer_Dashboard.customer_ui import CustomerDashboard
from Rider_Dashboard.rider_ui import RiderDashboard


class TaxiBookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Taxi Booking System')
        self.root.geometry('870x780')
        self.root.resizable()
        self.root.configure(bg='#ffffff')
        
        # Initialize both pages
        self.login_page = LoginPage(self.root, self.show_registration, self.show_dashboard)
        self.registration_page = RegistrationPage(self.root, self.show_login)
        self.dashboard = None
        
        # Show login page by default
        self.show_login()
    
    def show_login(self):
        if self.dashboard:
            # Destroy dashboard if it has a destroy method
            if hasattr(self.dashboard, 'destroy'):
                try:
                    self.dashboard.destroy()
                except Exception as e:
                    print(f"[DEBUG] Error destroying dashboard: {e}")
            # Hide sidebar and content frames if they exist
            if hasattr(self.dashboard, 'sidebar'):
                try:
                    self.dashboard.sidebar.pack_forget()
                except Exception:
                    pass
            if hasattr(self.dashboard, 'content'):
                try:
                    self.dashboard.content.pack_forget()
                except Exception:
                    pass
            self.dashboard = None
        """Switch to login page"""
        # Hide registration page and show login page
        self.registration_page.hide()
        self.login_page.show()
        # Clear registration fields when switching back to login
        self.registration_page.clear_fields()
        self.login_page.clear_fields()
    
    def show_registration(self):
        """Switch to registration page"""
        # Hide login page and show registration page
        self.login_page.hide()
        self.registration_page.show()
        self.login_page.txt_phone.delete(0, END)
        self.login_page.txt_password.delete(0, END)
        # Clear login fields when switching to registration
        self.login_page.clear_fields()
        
    def show_dashboard(self, username, role):
        self.login_page.hide()
        self.registration_page.hide()
        """Show the correct dashboard based on user role"""
        # role = None
        # conn = create_connection()
        # if conn:
        #     cursor = conn.cursor()
            
        #     # Check if admin
        # cursor.execute("SELECT role FROM users WHERE email=%s OR phone=%s", (username, username))
        # result = cursor.fetchone()
        # if result:
        #     role = result[0]  # role = Admin / Customer / Rider
        # cursor.close()
        # conn.close()
            
        # Hide login + registration
        self.login_page.hide()
        self.registration_page.hide()

        if role == "Admin":
            self.dashboard = AdminDashboard(self.root, username, logout_callback=self.show_login)
        elif role == "Customer":
            self.dashboard = CustomerDashboard(self.root, username, logout_callback=self.show_login)
        elif role == "Driver":
            self.dashboard = RiderDashboard(self.root, username, logout_callback=self.show_login)
        else:
            messagebox.showerror("Error", f"User role not found! Role={role}")


if __name__ == '__main__':
    # Update database schema if needed
    if not update_database():
        print("Warning: Could not update database schema. The application may not work correctly.")
    
    # Start the application
    root = Tk()
    app = TaxiBookingApp(root)
    root.mainloop()