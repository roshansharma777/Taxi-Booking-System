from tkinter import *
from login_page import LoginPage
from registration_page import RegistrationPage
from tkinter import messagebox
import mysql.connector
from db import create_connection
from theme_manager import save_theme_preference, get_theme_colors

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
        
        # Add ride_end_time column to bookings table if it doesn't exist
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'taxi_booking_system_test' 
            AND TABLE_NAME = 'bookings' 
            AND COLUMN_NAME = 'ride_end_time'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE bookings 
                ADD COLUMN ride_end_time DATETIME NULL
            """)
            conn.commit()
        
        # Add ride_status column to bookings table if it doesn't exist
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'taxi_booking_system_test' 
            AND TABLE_NAME = 'bookings' 
            AND COLUMN_NAME = 'ride_status'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE bookings 
                ADD COLUMN ride_status VARCHAR(50) NULL
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
from Admin_Dashboard. admin_ui import AdminDashboard
from Customer_Dashboard.customer_ui import CustomerDashboard
from Rider_Dashboard.rider_ui import RiderDashboard


class TaxiBookingApp:
    def __init__(self, root):
        self.root = root
        self.root. title('Taxi Booking System')
        self.root.geometry('800x780')
        self.root.resizable()
        self.root.configure(bg='#ffffff')
        
        # Initialize both pages
        self.login_page = LoginPage(self.root, self. show_registration, self.show_dashboard)
        self.registration_page = RegistrationPage(self. root, self.show_login)
        self.dashboard = None
        
        # Override the toggle_theme methods to sync between pages
        self.login_page.original_toggle_theme = self.login_page.toggle_theme
        self.login_page.toggle_theme = self.sync_theme_from_login
        
        self.registration_page.original_toggle_theme = self.registration_page.toggle_theme
        self.registration_page. toggle_theme = self.sync_theme_from_registration
        
        # Show login page by default
        self.show_login()
    
    def sync_theme_from_login(self):
        """Sync theme when toggled from login page"""
        # Save current form data from login page
        login_data = {}
        phone_email = self.login_page.txt_phone_email.get()
        password = self.login_page.txt_password.get()
        
        if phone_email != self.login_page. phone_placeholder:
            login_data['phone_email'] = phone_email
        if password != self.login_page.password_placeholder:
            login_data['password'] = password
        
        # Toggle login page theme (with data preservation)
        self.login_page.current_theme = "dark" if self.login_page.current_theme == "light" else "light"
        save_theme_preference(self.login_page.current_theme)
        self.login_page.theme_colors = get_theme_colors(self.login_page.current_theme)
        self.login_page.frame.destroy()
        self.login_page.create_widgets()
        
        # Restore login data
        if 'phone_email' in login_data:
            self.login_page.txt_phone_email. delete(0, END)
            self.login_page.txt_phone_email.insert(0, login_data['phone_email'])
            self.login_page. txt_phone_email.config(fg=self.login_page. entry_text_color)
        
        if 'password' in login_data:
            self. login_page.txt_password. delete(0, END)
            self.login_page.txt_password.insert(0, login_data['password'])
            self.login_page.txt_password. config(fg=self.login_page.entry_text_color, show="•")
        
        # Update registration page theme to match (without preserving data)
        if self.registration_page.current_theme != self.login_page.current_theme:
            self.registration_page.current_theme = self.login_page.current_theme
            self.registration_page.theme_colors = self.login_page.theme_colors
            self.registration_page. frame.destroy()
            self.registration_page.create_widgets()
    
    def sync_theme_from_registration(self):
        """Sync theme when toggled from registration page"""
        # Save current form data from registration page
        reg_data = {
            'fullname': self. registration_page.txt_fullname.get(),
            'email':  self.registration_page.txt_email.get(),
            'phone': self.registration_page.txt_phone.get(),
            'address': self.registration_page. txt_address.get(),
            'gender': self.registration_page.gender_var.get(),
            'password': self.registration_page.txt_password.get(),
            'confirm_password': self.registration_page.txt_confirm_password.get(),
            'role': self.registration_page. role_var.get()
        }
        
        # Toggle registration page theme (with data preservation)
        self.registration_page.current_theme = "dark" if self.registration_page.current_theme == "light" else "light"
        save_theme_preference(self.registration_page.current_theme)
        self.registration_page.theme_colors = get_theme_colors(self.registration_page.current_theme)
        self.registration_page.frame. destroy()
        self.registration_page.create_widgets()
        
        # Restore registration data
        self.registration_page.txt_fullname.insert(0, reg_data['fullname'])
        self.registration_page.txt_email.insert(0, reg_data['email'])
        self.registration_page. txt_phone.insert(0, reg_data['phone'])
        self.registration_page.txt_address.insert(0, reg_data['address'])
        self.registration_page.gender_var. set(reg_data['gender'])
        self.registration_page. txt_password.insert(0, reg_data['password'])
        self.registration_page.txt_confirm_password.insert(0, reg_data['confirm_password'])
        self.registration_page. role_var.set(reg_data['role'])
        
        # Update login page theme to match (without preserving data)
        if self.login_page. current_theme != self.registration_page.current_theme:
            self.login_page.current_theme = self.registration_page. current_theme
            self.login_page.theme_colors = self.registration_page.theme_colors
            self.login_page. frame.destroy()
            self.login_page.create_widgets()
    
    def show_login(self):
        if self.dashboard:
            # Destroy dashboard if it has a destroy method
            if hasattr(self.dashboard, 'destroy'):
                try:
                    self.dashboard. destroy()
                except Exception as e:
                    print(f"[DEBUG] Error destroying dashboard: {e}")
            # Hide sidebar and content frames if they exist
            if hasattr(self.dashboard, 'sidebar'):
                try:
                    self.dashboard. sidebar.pack_forget()
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
        # Clear login fields when switching to registration
        self.login_page.clear_fields()
        
    def show_dashboard(self, username, role):
        """Show the correct dashboard based on user role"""
        # Hide login + registration
        self.login_page.hide()
        self.registration_page.hide()

        if role == "Admin":
            self.dashboard = AdminDashboard(self.root, username, logout_callback=self.show_login)
        elif role == "Customer":
            self.dashboard = CustomerDashboard(self.root, username, logout_callback=self. show_login)
        elif role == "Driver":
            self.dashboard = RiderDashboard(self.root, username, logout_callback=self.show_login)
        else:
            messagebox.showerror("Error", f"User role not found!  Role={role}")


if __name__ == '__main__': 
    # Update database schema if needed
    if not update_database():
        print("Warning: Could not update database schema.  The application may not work correctly.")
    
    # Start the application
    root = Tk()
    app = TaxiBookingApp(root)
    root.mainloop()