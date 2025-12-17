from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from db import create_connection


class LoginPage:
    def __init__(self, root, switch_to_registration, switch_to_dashboard):
        self.root = root
        self.switch_to_registration = switch_to_registration
        self.switch_to_dashboard = switch_to_dashboard

        self.frame = None
        self.photo = None
        self.show_password_var = BooleanVar(value=False)

        self.txt_phone_email = None
        self.txt_password = None

        # Placeholder texts
        self.phone_placeholder = "Please enter phone no or email"
        self.password_placeholder = "Please enter password"

        self.create_widgets()

    def create_widgets(self):
        # Main frame fills the window
        self.frame = Frame(self.root, bg="#ffffff")
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Two-column layout with padding around everything
        main_container = Frame(self.frame, bg="#ffffff")
        main_container.pack(fill=BOTH, expand=True, padx=50, pady=40)

        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)

        # ================= LEFT: IMAGE (BIGGER HEIGHT) =================
        left_container = Frame(main_container, bg="#ffffff")
        left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 40))

        left_inner = Frame(left_container, bg="#ffffff")
        left_inner.place(relx=0.5, rely=0.45, anchor="center")

        try:
            bgimg = Image.open("City driver-pana.png")

            # Keep aspect ratio: wider and a bit taller than before
            target_w = 430
            w, h = bgimg.size
            scale = target_w / float(w)
            target_h = int(h * scale)

            max_h = 340  # allow more height than before (bigger image)
            if target_h > max_h:
                scale = max_h / float(h)
                target_w = int(w * scale)
                target_h = max_h

            bgimg = bgimg.resize((target_w, target_h), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(bgimg)

            img_label = Label(left_inner, image=self.photo, bg="#ffffff")
            img_label.pack()
        except Exception as e:
            print("Login image not found:", e)

        # ================= RIGHT: LOGIN CARD =================
        right_container = Frame(main_container, bg="#ffffff")
        right_container.grid(row=0, column=1, sticky="nsew")

        card_holder = Frame(right_container, bg="#ffffff")
        card_holder.place(relx=0.5, rely=0.5, anchor="center")

        # Shadow behind card
        shadow = Frame(card_holder, bg="#d0d0d0")
        shadow.place(x=8, y=8, width=360, height=440)

        login_frame = Frame(card_holder, bd=1, relief=RIDGE, bg="#ffffff")
        login_frame.pack()
        login_frame.configure(width=360, height=440)
        login_frame.pack_propagate(False)

        # Title
        title = Label(
            login_frame,
            text="Taxi Booking Login",
            font=("Times New Roman", 24, "bold"),
            bg="#ffffff",
            fg="#333333",
        )
        title.pack(pady=(28, 6))

        subtitle = Label(
            login_frame,
            text="Welcome back, please sign in",
            font=("Times New Roman", 11),
            bg="#ffffff",
            fg="#777777",
        )
        subtitle.pack(pady=(0, 18))

        # Content with inner padding
        content = Frame(login_frame, bg="#ffffff")
        content.pack(padx=28, pady=10, fill=BOTH, expand=True)

        # ========== PHONE / EMAIL ==========
        Label(
            content,
            text="Phone / Email",
            font=("Times New Roman", 14),
            bg="#ffffff",
            fg="#767171",
        ).pack(anchor=W, pady=(0, 4))

        self.txt_phone_email = Entry(
            content,
            font=("Times New Roman", 13),
            bg="#ECECEC",
            relief=FLAT,
            fg="grey",
        )
        self.txt_phone_email.pack(fill=X, ipady=6)

        # Insert placeholder
        self.txt_phone_email.insert(0, self.phone_placeholder)

        self.txt_phone_email.bind("<FocusIn>", self._clear_phone_placeholder)
        self.txt_phone_email.bind("<FocusOut>", self._add_phone_placeholder)

        # ========== PASSWORD ==========
        Label(
            content,
            text="Password",
            font=("Times New Roman", 14),
            bg="#ffffff",
            fg="#767171",
        ).pack(anchor=W, pady=(14, 4))

        password_frame = Frame(content, bg="#ECECEC")
        password_frame.pack(fill=X)

        self.txt_password = Entry(
            password_frame,
            font=("Times New Roman", 13),
            bg="#ECECEC",
            show="",              # show text for placeholder
            relief=FLAT,
            bd=0,
            fg="grey",
        )
        self.txt_password.pack(side=LEFT, fill=BOTH, expand=True, ipady=6, padx=(6, 0))

        # Insert placeholder
        self.txt_password.insert(0, self.password_placeholder)

        self.txt_password.bind("<FocusIn>", self._clear_password_placeholder)
        self.txt_password.bind("<FocusOut>", self._add_password_placeholder)

        show_password_btn = Button(
            password_frame,
            text="👁",
            font=("Arial", 10),
            bg="#ECECEC",
            fg="#555555",
            relief=FLAT,
            bd=0,
            cursor="hand2",
            command=self.toggle_password,
        )
        show_password_btn.pack(side=RIGHT, padx=6)

        # ========== LOGIN BUTTON ==========
        btn_login = Button(
            content,
            text="Log In",
            font=("Arial Rounded MT Bold", 14),
            bg="#00B0F0",
            fg="#ffffff",
            activebackground="#00B0F0",
            activeforeground="#ffffff",
            cursor="hand2",
            relief=FLAT,
            command=self.login,
        )
        btn_login.pack(pady=(20, 10), ipady=6, ipadx=30)

        # ========== CLEAN "OR" DIVIDER ==========
        divider_frame = Frame(content, bg="#ffffff")
        divider_frame.pack(fill=X, pady=(8, 12))

        line_left = Frame(divider_frame, bg="lightgrey", height=1)
        line_left.pack(side=LEFT, fill=X, expand=True, padx=(0, 8), pady=(8, 0))

        or_label = Label(
            divider_frame,
            text="Or",
            bg="#ffffff",
            fg="lightgrey",
            font=("Times New Roman", 12, "bold"),
        )
        or_label.pack(side=LEFT)

        line_right = Frame(divider_frame, bg="lightgrey", height=1)
        line_right.pack(side=LEFT, fill=X, expand=True, padx=(8, 0), pady=(8, 0))

        # ========== REGISTER LINK ==========
        btn_register = Button(
            content,
            text="Register Now",
            font=("Times New Roman", 13, "bold", "underline"),
            bg="#ffffff",
            fg="#00B0F0",
            bd=0,
            activebackground="#ffffff",
            activeforeground="#00B0F0",
            cursor="hand2",
            command=self.switch_to_registration,
        )
        btn_register.pack(pady=(4, 0))

        # Enter key bindings
        self.txt_phone_email.bind("<Return>", lambda e: self.txt_password.focus())
        self.txt_password.bind("<Return>", lambda e: self.login())

    # ================= PLACEHOLDER HANDLERS =================
    def _clear_phone_placeholder(self, event):
        if self.txt_phone_email.get() == self.phone_placeholder:
            self.txt_phone_email.delete(0, END)
            self.txt_phone_email.config(fg="black")

    def _add_phone_placeholder(self, event):
        if not self.txt_phone_email.get().strip():
            self.txt_phone_email.insert(0, self.phone_placeholder)
            self.txt_phone_email.config(fg="grey")

    def _clear_password_placeholder(self, event):
        if self.txt_password.get() == self.password_placeholder:
            self.txt_password.delete(0, END)
            self.txt_password.config(fg="black", show="•" if not self.show_password_var.get() else "")

    def _add_password_placeholder(self, event):
        if not self.txt_password.get().strip():
            self.txt_password.config(show="", fg="grey")
            self.txt_password.insert(0, self.password_placeholder)

    # ================= LOGIC =================
    def toggle_password(self):
        """Toggle password visibility (only when real password is present)."""
        current_text = self.txt_password.get()
        is_placeholder = current_text == self.password_placeholder and self.txt_password.cget("fg") == "grey"

        if is_placeholder:
            # Do nothing when only placeholder is shown
            return

        if self.show_password_var.get():
            # Currently shown plain, hide it
            self.txt_password.config(show="•")
            self.show_password_var.set(False)
        else:
            # Currently hidden, show it
            self.txt_password.config(show="")
            self.show_password_var.set(True)

    def login(self):
        phone_email = self.txt_phone_email.get().strip()
        password = self.txt_password.get()

        # Ignore placeholder text
        if phone_email == self.phone_placeholder:
            phone_email = ""
        if password == self.password_placeholder:
            password = ""

        if not phone_email or not password:
            messagebox.showerror("Error", "All fields are required!")
            return

        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    SELECT full_name, role
                    FROM users
                    WHERE (email=%s OR phone=%s) AND password=%s
                    """,
                    (phone_email, phone_email, password),
                )
                result = cursor.fetchone()

                if result:
                    full_name, role = result
                    messagebox.showinfo("Success", f"Welcome back, {full_name}!")
                    self.clear_fields()
                    self.switch_to_dashboard(full_name, role)
                else:
                    messagebox.showerror("Error", "Invalid email/phone or password!\n\nPlease check your credentials and try again.")
                    self.txt_password.delete(0, END)
                    self.txt_password.insert(0, self.password_placeholder)
                    self.txt_password.config(fg="grey", show="")
            except Exception as e:
                messagebox.showerror("Error", f"Login failed: {e}")
            finally:
                cursor.close()
                conn.close()

    def show(self):
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)

    def hide(self):
        self.frame.place_forget()

    def get_credentials(self):
        phone_email = self.txt_phone_email.get()
        password = self.txt_password.get()
        if phone_email == self.phone_placeholder:
            phone_email = ""
        if password == self.password_placeholder:
            password = ""
        return {
            "phone_or_email": phone_email,
            "password": password,
        }

    def clear_fields(self):
        # Phone/email
        self.txt_phone_email.delete(0, END)
        self.txt_phone_email.insert(0, self.phone_placeholder)
        self.txt_phone_email.config(fg="grey")

        # Password
        self.txt_password.delete(0, END)
        self.txt_password.insert(0, self.password_placeholder)
        self.txt_password.config(fg="grey", show="")

        self.show_password_var.set(False)