from tkinter import *
from tkinter import messagebox
from db import create_connection
from theme_manager import get_theme_colors, save_theme_preference, get_theme_preference
import re

class RegistrationPage: 
    def __init__(self, root, switch_to_login):
        self.root = root
        self.switch_to_login = switch_to_login
        self.gender_var = StringVar(value="Male")
        self.frame = None
        
        # Theme management
        self.current_theme = get_theme_preference()
        self.theme_colors = get_theme_colors(self.current_theme)
        self.theme_toggle_btn = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame for registration page
        self.frame = Frame(self.root, bg=self. theme_colors. get("content_bg", "#f5f5f5"))
        
        # Theme toggle button - positioned at top-left with subtle styling
        toggle_bg = "#f0f0f0" if self.current_theme == "light" else "#2d3748"
        toggle_fg = "#333333" if self.current_theme == "light" else "#e2e8f0"
        
        self.theme_toggle_btn = Button(
            self. frame,
            text="🌙" if self.current_theme == "light" else "☀️",
            font=("Arial", 14),
            bg=toggle_bg,
            fg=toggle_fg,
            relief=FLAT,
            bd=0,
            cursor="hand2",
            command=self.toggle_theme,
            width=3,
            height=1,
            highlightthickness=1,
            highlightbackground="#d0d0d0" if self.current_theme == "light" else "#4a5568",
            highlightcolor="#d0d0d0" if self.current_theme == "light" else "#4a5568"
        )
        # Position it at top-left corner
        self.theme_toggle_btn.place(x=20, y=20)
        
        # Create canvas for scrolling
        canvas = Canvas(self.frame, bg=self.theme_colors.get("content_bg", "#f5f5f5"), highlightthickness=0)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Add vertical scrollbar
        scrollbar_bg = "#e5e7eb" if self.current_theme == "light" else "#475569"
        v_scrollbar = Scrollbar(self.frame, orient=VERTICAL, command=canvas.yview, bg=scrollbar_bg)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Add horizontal scrollbar
        h_scrollbar = Scrollbar(self.frame, orient=HORIZONTAL, command=canvas.xview, bg=scrollbar_bg)
        h_scrollbar.pack(side=BOTTOM, fill=X)
        
        # Configure canvas
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Create scrollable frame inside canvas
        scrollable_frame = Frame(canvas, bg=self.theme_colors. get("content_bg", "#f5f5f5"))
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        
        # Center the scrollable frame
        scrollable_frame.pack(expand=True)
        
        # Registration Frame (centered in scrollable area)
        container = Frame(scrollable_frame, bg=self.theme_colors. get("content_bg", "#f5f5f5"))
        container.pack(pady=20, expand=True)
        
        # Shadow effect
        shadow_color = "#d0d0d0" if self.current_theme == "light" else "#1a1a1a"
        shadow_frame = Frame(container, bg=shadow_color)
        shadow_frame.place(x=5, y=5, width=450, height=600)
        
        reg_frame = Frame(container, bd=2, relief=RIDGE, bg=self.theme_colors.get("card_bg", "#ffffff"))
        reg_frame.pack()
        
        # Frame Title
        title = Label(reg_frame, text="Registration", font=("Times New Roman", 28, "bold"), 
                     bg=self.theme_colors.get("card_bg", "#ffffff"), 
                     fg=self.theme_colors.get("card_text", "#333333"))
        title.pack(pady=15)
        
        # Content container with padding
        content = Frame(reg_frame, bg=self.theme_colors.get("card_bg", "#ffffff"))
        content.pack(padx=40, pady=5)
        
        # Determine entry colors based on theme
        entry_bg = "#ECECEC" if self.current_theme == "light" else "#475569"
        entry_fg = "#333333" if self.current_theme == "light" else "#f1f5f9"
        label_fg = self.theme_colors.get("card_text_secondary", "#555555")
        
        # Full Name
        lbl_Fullname = Label(content, text="Full Name", font=("Times New Roman", 14), 
                         bg=self.theme_colors.get("card_bg", "#ffffff"), fg=label_fg)
        lbl_Fullname.pack(anchor=W, pady=(5, 3))
        
        self.txt_fullname = Entry(content, font=("times new roman", 13), bg=entry_bg, 
                                 fg=entry_fg, relief=FLAT, insertbackground=entry_fg)
        self.txt_fullname.pack(fill=X, ipady=6)
        
        # Email
        lbl_Email = Label(content, text="Email", font=("Times New Roman", 14), 
                         bg=self.theme_colors. get("card_bg", "#ffffff"), fg=label_fg)
        lbl_Email.pack(anchor=W, pady=(10, 3))
        
        self.txt_email = Entry(content, font=("times new roman", 13), bg=entry_bg, 
                              fg=entry_fg, relief=FLAT, insertbackground=entry_fg)
        self.txt_email.pack(fill=X, ipady=6)
        
        # Phone Number
        lbl_phone = Label(content, text="Phone Number", font=("Times New Roman", 14), 
                          bg=self.theme_colors. get("card_bg", "#ffffff"), fg=label_fg)
        lbl_phone.pack(anchor=W, pady=(10, 3))
        
        self.txt_phone = Entry(content, font=("times new roman", 13), bg=entry_bg, 
                              fg=entry_fg, relief=FLAT, insertbackground=entry_fg)
        self.txt_phone.pack(fill=X, ipady=6)
        
        # Address
        lbl_address = Label(content, text="Address", font=("Times New Roman", 14), 
                            bg=self.theme_colors. get("card_bg", "#ffffff"), fg=label_fg)
        lbl_address.pack(anchor=W, pady=(10, 3))
        
        self.txt_address = Entry(content, font=("times new roman", 13), bg=entry_bg, 
                                fg=entry_fg, relief=FLAT, insertbackground=entry_fg)
        self.txt_address.pack(fill=X, ipady=6)
        
        # Gender and Role in same row
        gender_role_frame = Frame(content, bg=self.theme_colors.get("card_bg", "#ffffff"))
        gender_role_frame. pack(fill=X, pady=(10, 0))
        
        # Gender (left side)
        gender_frame = Frame(gender_role_frame, bg=self.theme_colors.get("card_bg", "#ffffff"))
        gender_frame. pack(side=LEFT, fill=X, expand=True)
        
        lbl_gender = Label(gender_frame, text="Gender", font=("Times New Roman", 14), 
                          bg=self.theme_colors. get("card_bg", "#ffffff"), fg=label_fg)
        lbl_gender.pack(anchor=W, pady=(0, 5))
        
        gender_options = Frame(gender_frame, bg=self.theme_colors.get("card_bg", "#ffffff"))
        gender_options.pack(anchor=W)
        
        radio_fg = self.theme_colors.get("card_text", "#333333")
        Radiobutton(gender_options, text="Male", variable=self. gender_var, value="Male", 
                   font=("Times New Roman", 12), bg=self.theme_colors.get("card_bg", "#ffffff"),
                   fg=radio_fg, selectcolor=entry_bg, activebackground=self.theme_colors.get("card_bg", "#ffffff"),
                   activeforeground=radio_fg).pack(side=LEFT, padx=(0, 15))
        Radiobutton(gender_options, text="Female", variable=self. gender_var, value="Female", 
                   font=("Times New Roman", 12), bg=self.theme_colors.get("card_bg", "#ffffff"),
                   fg=radio_fg, selectcolor=entry_bg, activebackground=self.theme_colors.get("card_bg", "#ffffff"),
                   activeforeground=radio_fg).pack(side=LEFT)
        
        # Role (right side)
        role_frame = Frame(gender_role_frame, bg=self.theme_colors.get("card_bg", "#ffffff"))
        role_frame.pack(side=LEFT, fill=X, expand=True)
        
        lbl_role = Label(role_frame, text="Role", font=("Times New Roman", 14), 
                        bg=self.theme_colors. get("card_bg", "#ffffff"), fg=label_fg)
        lbl_role.pack(anchor=W, pady=(0, 5))
        
        self.role_var = StringVar(value="Customer")
        role_menu = OptionMenu(role_frame, self.role_var, "Admin", "Customer", "Driver")
        role_menu.config(font=("Times New Roman", 11), bg=entry_bg, fg=entry_fg, 
                        width=12, relief=FLAT, activebackground=entry_bg, 
                        activeforeground=entry_fg, highlightthickness=0)
        role_menu["menu"]. config(bg=entry_bg, fg=entry_fg)
        role_menu.pack(anchor=W)
        
        # Password
        lbl_password = Label(content, text="Password", font=("Times New Roman", 14), 
                             bg=self.theme_colors. get("card_bg", "#ffffff"), fg=label_fg)
        lbl_password.pack(anchor=W, pady=(10, 3))
        
        password_frame = Frame(content, bg=entry_bg)
        password_frame.pack(fill=X)
        
        self.txt_password = Entry(password_frame, font=("times new roman", 13), bg=entry_bg, 
                                 fg=entry_fg, show="•", relief=FLAT, bd=0, insertbackground=entry_fg)
        self.txt_password. pack(side=LEFT, fill=BOTH, expand=True, ipady=6, padx=(5, 0))
        
        self.show_password_var = BooleanVar(value=False)
        eye_icon_color = "#555555" if self.current_theme == "light" else "#b0b0b0"
        show_password_btn = Button(password_frame, text="👁", font=("Arial", 12), bg=entry_bg, 
                                   fg=eye_icon_color, relief=FLAT, bd=0, cursor="hand2",
                                   command=self.toggle_password)
        show_password_btn. pack(side=RIGHT, padx=5)
        
        # Confirm Password
        lbl_confirm_password = Label(content, text="Confirm Password", font=("Times New Roman", 14), 
                                     bg=self.theme_colors. get("card_bg", "#ffffff"), fg=label_fg)
        lbl_confirm_password. pack(anchor=W, pady=(10, 3))
        
        confirm_password_frame = Frame(content, bg=entry_bg)
        confirm_password_frame.pack(fill=X)
        
        self.txt_confirm_password = Entry(confirm_password_frame, font=("times new roman", 13), 
                                         bg=entry_bg, fg=entry_fg, show="•", relief=FLAT, bd=0,
                                         insertbackground=entry_fg)
        self.txt_confirm_password.pack(side=LEFT, fill=BOTH, expand=True, ipady=6, padx=(5, 0))
        
        self. show_confirm_password_var = BooleanVar(value=False)
        show_confirm_password_btn = Button(confirm_password_frame, text="👁", font=("Arial", 12), 
                                          bg=entry_bg, fg=eye_icon_color, relief=FLAT, bd=0, 
                                          cursor="hand2", command=self.toggle_confirm_password)
        show_confirm_password_btn.pack(side=RIGHT, padx=5)
        
        # Register Button
        btn_register = Button(content, text="Register", font=("arial round mt bold", 14), 
                              bg=self.theme_colors. get("accent", "#00B0F0"), fg="#ffffff", 
                              activebackground=self.theme_colors.get("accent", "#00B0F0"), 
                              cursor="hand2", activeforeground="#ffffff", command=self.register,
                              relief=FLAT, bd=0)
        btn_register.pack(pady=15, ipady=6, ipadx=30)
        
        # Already have account message
        login_frame = Frame(content, bg=self.theme_colors.get("card_bg", "#ffffff"))
        login_frame.pack(pady=(0, 10))
        
        message = Label(login_frame, text="Already have an account?", 
                        font=("times new roman", 10), 
                        bg=self.theme_colors.get("card_bg", "#ffffff"), 
                        fg=self.theme_colors.get("card_text_secondary", "#666666"))
        message.pack(side=LEFT)
        
        # Login Button
        btn_login = Button(login_frame, text="Login", 
                           font=("Times New Roman", 10, "bold", "underline"), 
                           bg=self.theme_colors. get("card_bg", "#ffffff"), 
                           fg=self.theme_colors.get("accent", "#00B0F0"), bd=0, 
                           activebackground=self.theme_colors.get("card_bg", "#ffffff"), 
                           cursor="hand2", 
                           activeforeground=self.theme_colors.get("accent", "#00B0F0"), 
                           command=self.switch_to_login)
        btn_login.pack(side=LEFT, padx=5)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def toggle_password(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.txt_password.config(show="")
            self.show_password_var.set(False)
        else:
            self.txt_password.config(show="•")
            self.show_password_var.set(True)
    
    def toggle_confirm_password(self):
        """Toggle confirm password visibility"""
        if self.show_confirm_password_var.get():
            self.txt_confirm_password.config(show="")
            self.show_confirm_password_var.set(False)
        else:
            self.txt_confirm_password. config(show="•")
            self.show_confirm_password_var.set(True)
    
    def toggle_theme(self, preserve_data=True):
        """Toggle between light and dark theme"""
        form_data = {}
        
        # Only save form data if requested (not during sync from other page)
        if preserve_data: 
            form_data = {
                'fullname': self.txt_fullname.get(),
                'email': self.txt_email.get(),
                'phone': self.txt_phone. get(),
                'address': self.txt_address.get(),
                'gender': self.gender_var.get(),
                'password': self.txt_password.get(),
                'confirm_password':  self.txt_confirm_password. get(),
                'role': self.role_var.get()
            }
        
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        save_theme_preference(self.current_theme)
        self.theme_colors = get_theme_colors(self. current_theme)
        
        # Recreate widgets with new theme
        self.frame.destroy()
        self.create_widgets()
        
        # Restore form data only if we preserved it
        if preserve_data and form_data:
            self. txt_fullname.insert(0, form_data['fullname'])
            self.txt_email.insert(0, form_data['email'])
            self.txt_phone.insert(0, form_data['phone'])
            self.txt_address.insert(0, form_data['address'])
            self.gender_var. set(form_data['gender'])
            self.txt_password. insert(0, form_data['password'])
            self.txt_confirm_password.insert(0, form_data['confirm_password'])
            self.role_var. set(form_data['role'])
    
    def register(self):
        # Get all registration data
        fullname = self. txt_fullname.get().strip()
        email = self. txt_email.get().strip()
        phone = self.txt_phone.get().strip()
        address = self.txt_address. get().strip()
        gender = self.gender_var.get()
        password = self.txt_password.get()
        confirm_password = self.txt_confirm_password.get()
        role = self.role_var.get()
        
        # Validate inputs
        if not all([fullname, email, phone, address, gender, password, confirm_password]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if '@' not in email or '.' not in email:
            messagebox.showerror("Error", "Please enter a valid email address!")
            return
        
        if not phone.isdigit() or len(phone) < 10:
            messagebox. showerror("Error", "Please enter a valid phone number (at least 10 digits)!")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        # Password Strength Check
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            return
        if not re.search(r'[A-Z]', password):
             messagebox.showerror("Error", "Password must contain at least one uppercase letter!")
             return

        if not re.search(r'\d', password):
            messagebox.showerror("Error", "Password must contain at least one number!")
            return
        
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (full_name, email, phone, address, gender, password, role) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (fullname, email, phone, address, gender, password, role)
                )
                conn.commit()
                messagebox.showinfo("Success", "Registration successful! Please login.")
                self.clear_fields()
                self.switch_to_login()
            except Exception as e: 
                messagebox.showerror("Error", f"Registration failed: {str(e)}")
            finally:
                cursor.close()
                conn.close()

    def show(self):
        self.frame. pack(fill=BOTH, expand=True)

    def hide(self):
        self.frame.pack_forget()

    def clear_fields(self):
        self.txt_fullname.delete(0, END)
        self.txt_email.delete(0, END)
        self.txt_phone.delete(0, END)
        self.txt_address.delete(0, END)
        self.gender_var.set("Male")
        self.txt_password.delete(0, END)
        self.txt_confirm_password.delete(0, END)
        self.role_var.set("Customer")