from tkinter import *
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme_manager import get_theme_colors, save_theme_preference, get_theme_preference
from Customer_Dashboard.customer_service import CustomerService


class CustomerDashboard:
    def __init__(self, root, customer_id, logout_callback=None):
        self.root = root
        self.logout_callback = logout_callback

        # Initialize service layer
        try:
            self.service = CustomerService(customer_id)
            info = self.service.get_basic_info()
            self.user_full_name = info[0] if info else ""
            self.photo_path = info[1] if info else None
            self.customer_id = self.service.customer_id
        except Exception as e:
            messagebox.showerror("User Error", f"Failed to initialize customer: {e}")
            print(f"[DEBUG] Failed to initialize customer {customer_id}: {e}")
            self.user_full_name = ""
            self.photo_path = None
            self.customer_id = None

        # Cache for image reference
        self.profile_img_tk = None

        # Initialize theme
        self.current_theme = get_theme_preference()
        self.colors = get_theme_colors(self.current_theme)
        self._update_color_vars()

        self.root.title("Customer Dashboard")
        self.root.geometry("1000x650")
        self.root.config(bg=self.color_content_bg)

        # -------- TABLE STYLE (for bookings list) --------
        try:
            style = ttk.Style(self.root)
            style.configure(
                "Customer.Treeview",
                rowheight=22,
                padding=(2, 1),
            )
            style.configure(
                "Customer.Treeview.Heading",
                padding=(4, 2),
            )
        except Exception:
            pass

        # ------------------ MENU BAR ------------------
        self.mainmenu = Menu(self.root)

        filemenu = Menu(self.mainmenu, tearoff=0)
        filemenu.add_command(label='New', command=self.doNothing)
        filemenu.add_command(label='Open', command=self.doNothing)
        filemenu.add_command(label='Save', command=self.doNothing)
        filemenu.add_command(label='Save as...', command=self.doNothing)
        filemenu.add_command(label='Close', command=self.doNothing)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.root.quit)
        self.mainmenu.add_cascade(label='File', menu=filemenu)

        editmenu = Menu(self.mainmenu, tearoff=0)
        editmenu.add_command(label='Undo', command=self.doNothing)
        editmenu.add_command(label='Redo', command=self.doNothing)
        editmenu.add_separator()
        editmenu.add_command(label='Cut', command=self.doNothing)
        editmenu.add_command(label='Copy', command=self.doNothing)
        editmenu.add_command(label='Paste', command=self.doNothing)
        self.mainmenu.add_cascade(label='Edit', menu=editmenu)

        viewmenu = Menu(self.mainmenu, tearoff=0)
        viewmenu.add_command(label='Refresh Dashboard', command=self.show_dashboard)
        viewmenu.add_command(label='Show Bookings', command=self.show_bookings)
        viewmenu.add_command(label='Show Profile', command=self.show_profile)
        self.mainmenu.add_cascade(label='View', menu=viewmenu)

        toolsmenu = Menu(self.mainmenu, tearoff=0)
        toolsmenu.add_command(label='Settings', command=self.show_settings)
        toolsmenu.add_command(label='Support', command=self.show_support)
        toolsmenu.add_command(label='Export Data', command=self.doNothing)
        self.mainmenu.add_cascade(label='Tools', menu=toolsmenu)

        helpmenu = Menu(self.mainmenu, tearoff=0)
        helpmenu.add_command(label='User Guide', command=self.doNothing)
        helpmenu.add_command(label='About', command=self.doNothing)
        helpmenu.add_command(label='Contact Support', command=self.show_support)
        self.mainmenu.add_cascade(label='Help', menu=helpmenu)

        self.root.config(menu=self.mainmenu)

        # ----------------- MAIN LAYOUT ------------------
        self.sidebar = Frame(self.root, width=220, bg=self.color_sidebar_bg)
        self.sidebar.pack(side=LEFT, fill=Y)

        self.content = Frame(self.root, bg=self.color_content_bg)
        self.content.pack(side=RIGHT, fill=BOTH, expand=True)

        # Apply theme to treeview styles
        self._apply_treeview_theme()
        
        # Track current page for theme refresh
        self._current_page_method = self.show_dashboard
        
        self.build_sidebar()
        self.show_dashboard()

    # ------------- IMAGE UTIL -------------
    def _load_circular_image(self, path, size=(100, 100)):
        """Load image from path, crop to circle, return PhotoImage."""
        try:
            img = Image.open(path).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)

            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            img.putalpha(mask)

            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"[DEBUG] _load_circular_image error: {e}")
            return None

    # ------------------ SIDEBAR ------------------
    def build_sidebar(self):
        Label(
            self.sidebar,
            text="Customer Menu",
            fg="white",
            bg=self.color_sidebar_bg,
            font=("Arial", 16, "bold"),
            pady=20
        ).pack()

        btns = [
            ("Dashboard", self.show_dashboard),
            ("Book Taxi", self.show_book_taxi),
            ("My Bookings", self.show_bookings),
            ("Profile", self.show_profile),
            ("Support", self.show_support),
            ("Settings", self.show_settings),
        ]

        for text, cmd in btns:
            Button(
                self.sidebar,
                text=text,
                command=cmd,
                font=("Arial", 12),
                fg="white",
                bg=self.color_sidebar_btn,
                bd=0,
                relief="flat",
                activebackground=self.color_sidebar_btn_active,
                cursor="hand2",
                width=20,
                height=2
            ).pack(pady=5)

        # Theme toggle button
        self.theme_toggle_btn = Button(
            self.sidebar,
            text="🌙 Dark Mode" if self.current_theme == "light" else "☀️ Light Mode",
            width=20,
            bg=self.color_sidebar_btn,
            fg="white",
            font=("Arial", 11),
            relief="flat",
            cursor="hand2",
            activebackground=self.color_sidebar_btn_active,
            command=self._toggle_theme
        )
        self.theme_toggle_btn.pack(pady=10)

        Button(
            self.sidebar,
            text="Logout",
            command=self.logout,
            font=("Arial", 12),
            fg="white",
            bg="#ef4444",
            bd=0,
            relief="flat",
            activebackground="#dc2626",
            cursor="hand2",
            width=20,
            height=2
        ).pack(side=BOTTOM, pady=20)

    def _update_color_vars(self):
        """Update color variables from theme."""
        self.color_sidebar_bg = self.colors["sidebar_bg"]
        self.color_sidebar_btn = self.colors["sidebar_btn"]
        self.color_sidebar_btn_active = self.colors["sidebar_btn_active"]
        self.color_content_bg = self.colors["content_bg"]
        self.color_accent = self.colors["accent"]
        self.color_text_primary = self.colors["text_primary"]
        self.color_text_secondary = self.colors["text_secondary"]
        self.color_card_bg = self.colors["card_bg"]
        self.color_card_text = self.colors["card_text"]
        self.color_card_text_secondary = self.colors["card_text_secondary"]

    def _apply_treeview_theme(self):
        """Apply theme to treeview styles."""
        try:
            style = ttk.Style(self.root)
            style.configure(
                "Customer.Treeview",
                rowheight=22,
                padding=(2, 1),
                background=self.colors["treeview_bg"],
                foreground=self.colors["treeview_fg"],
                fieldbackground=self.colors["treeview_bg"]
            )
            style.configure(
                "Customer.Treeview.Heading",
                padding=(4, 2),
                background=self.colors["sidebar_btn"],
                foreground="white"
            )
        except Exception:
            pass

    def _toggle_theme(self):
        """Toggle between light and dark theme."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        save_theme_preference(self.current_theme)
        self.colors = get_theme_colors(self.current_theme)
        self._update_color_vars()
        
        # Update root window
        self.root.configure(bg=self.color_content_bg)
        
        # Update sidebar
        self.sidebar.configure(bg=self.color_sidebar_bg)
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, Button):
                if widget != self.theme_toggle_btn and widget.cget("text") != "Logout":
                    widget.configure(bg=self.color_sidebar_btn, activebackground=self.color_sidebar_btn_active)
        
        # Update theme toggle button
        self.theme_toggle_btn.configure(
            text="🌙 Dark Mode" if self.current_theme == "light" else "☀️ Light Mode",
            bg=self.color_sidebar_btn,
            activebackground=self.color_sidebar_btn_active
        )
        
        # Update content area
        self.content.configure(bg=self.color_content_bg)
        
        # Reapply treeview theme
        self._apply_treeview_theme()
        
        # Refresh current page
        if hasattr(self, '_current_page_method'):
            self._current_page_method()
        else:
            self.show_dashboard()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # -------- shared helper: make Treeview columns sortable --------
    def _make_treeview_sortable(self, tree, cols, numeric_cols=None):
        """
        Enable click-to-sort on ttk.Treeview headers.
        numeric_cols: iterable of column ids that should sort numerically.
        """
        if numeric_cols is None:
            numeric_cols = set()
        else:
            numeric_cols = set(numeric_cols)

        def _cast(val, col):
            if col in numeric_cols:
                try:
                    return int(val)
                except Exception:
                    return 0
            return val.lower() if isinstance(val, str) else val

        def _sort(col, reverse=False):
            data = [(tree.set(k, col), k) for k in tree.get_children("")]
            data.sort(key=lambda t: _cast(t[0], col), reverse=reverse)
            for idx, (_, k) in enumerate(data):
                tree.move(k, "", idx)
            tree.heading(col, command=lambda: _sort(col, not reverse))

        for c in cols:
            tree.heading(c, command=lambda col=c: _sort(col, False))

    # ------------------ DASHBOARD ------------------
    def show_dashboard(self):
        self._current_page_method = self.show_dashboard
        self.clear_content()
        welcome_name = self.user_full_name if self.user_full_name else "Customer"

        # Hero
        Label(
            self.content,
            text=f"Welcome, {welcome_name}!",
            font=("Arial", 26, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=(20, 8))

        Label(
            self.content,
            text="Quick glance at your booking activity",
            font=("Arial", 12),
            bg=self.color_content_bg,
            fg=self.color_text_secondary
        ).pack()

        # Stats cards
        cards = Frame(self.content, bg=self.color_content_bg)
        cards.pack(pady=20, padx=20, fill=X)

        try:
            rows = self.service.get_bookings()
        except Exception:
            rows = []

        total = len(rows)
        completed = sum(1 for r in rows if len(r) > 5 and str(r[5]).lower() == "completed")
        cancelled = sum(1 for r in rows if len(r) > 5 and str(r[5]).lower() == "cancelled")
        active = total - completed - cancelled

        def card(parent, emoji, value, label, color):
            outer = Frame(parent, bg=self.color_card_bg, relief="flat", bd=1)
            outer.pack(side=LEFT, padx=10, fill=BOTH, expand=True)
            inner = Frame(outer, bg=self.color_card_bg)
            inner.pack(padx=20, pady=20, fill=BOTH)
            Label(inner, text=emoji, font=("Arial", 30), bg=self.color_card_bg).pack()
            Label(inner, text=str(value), font=("Arial", 28, "bold"), bg=self.color_card_bg, fg=color).pack()
            Label(inner, text=label, font=("Arial", 12), bg=self.color_card_bg, fg=self.color_card_text_secondary).pack()

        card(cards, "🧳", total, "Total Bookings", "#2563eb")
        card(cards, "✅", completed, "Completed", "#16a34a")
        card(cards, "🕒", active, "Active / Upcoming", "#f59e0b")

        # Hint text
        Label(
            self.content,
            text="Use the left menu to book a taxi or view booking history.",
            font=("Arial", 12),
            bg=self.color_content_bg,
            fg="#4b5563"
        ).pack(pady=(10, 0))

    # ------------------ PROFILE PAGE ------------------
    def show_profile(self):
        self.clear_content()

        Label(
            self.content,
            text="My Profile",
            font=("Arial", 18, "bold"),
            bg=self.color_content_bg
        ).pack(pady=20)

        if not self.customer_id:
            messagebox.showerror("Error", "Customer ID not resolved. Cannot load profile.")
            return

        try:
            row = self.service.get_profile()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch profile: {e}")
            return

        if not row:
            messagebox.showerror("Error", "User not found!")
            return

        if len(row) == 7:
            full_name, email, phone, address, gender, role, db_photo_path = row
            self.photo_path = db_photo_path
        else:
            full_name, email, phone, address, gender, role = row

        # ---------- Photo + Upload ----------
        photo_frame = Frame(self.content, bg=self.color_content_bg)
        photo_frame.pack(pady=10)

        canvas_size = 120
        avatar_canvas = Canvas(
            photo_frame,
            width=canvas_size,
            height=canvas_size,
            bg=self.color_content_bg,
            highlightthickness=0
        )
        avatar_canvas.pack()

        radius = 50
        center_x = center_y = canvas_size // 2
        avatar_canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill="#d1d5db",
            outline="#9ca3af",
            width=2,
            tags="avatar_bg"
        )

        def refresh_avatar():
            avatar_canvas.delete("avatar_img")
            avatar_canvas.delete("avatar_initial")
            if self.photo_path and os.path.isfile(self.photo_path):
                img_tk = self._load_circular_image(self.photo_path, size=(100, 100))
                if img_tk:
                    self.profile_img_tk = img_tk
                    avatar_canvas.create_image(
                        center_x,
                        center_y,
                        image=self.profile_img_tk,
                        tags="avatar_img"
                    )
                    return
            # fallback: first letter
            avatar_canvas.create_text(
                center_x,
                center_y,
                text=(full_name[:1].upper() if full_name else "?"),
                font=("Arial", 32, "bold"),
                fill="#4b5563",
                tags="avatar_initial"
            )

        refresh_avatar()

        def upload_photo():
            filetypes = [
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*"),
            ]
            filepath = filedialog.askopenfilename(
                title="Select Profile Photo",
                filetypes=filetypes
            )
            if not filepath:
                return

            try:
                photos_dir = "profile_photos"
                os.makedirs(photos_dir, exist_ok=True)
                ext = os.path.splitext(filepath)[1]
                filename = f"user_{self.customer_id}{ext}"
                dest_path = os.path.join(photos_dir, filename)

                with open(filepath, "rb") as src, open(dest_path, "wb") as dst:
                    dst.write(src.read())

                self.photo_path = dest_path
                self.service.update_photo_path(dest_path)
                messagebox.showinfo("Success", "Profile photo updated.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update photo: {e}")
                return

            refresh_avatar()

        Button(
            photo_frame,
            text="Upload Photo",
            bg=self.color_accent,
            fg="white",
            font=("Arial", 10, "bold"),
            command=upload_photo
        ).pack(pady=5)

        # ---------- Text fields ----------
        frame = Frame(self.content, bg=self.color_content_bg)
        frame.pack(pady=10)

        labels = ["Full Name", "Email", "Phone", "Address", "Gender", "Role"]
        values = [full_name, email, phone, address, gender, role]
        entries = {}

        for i, lab in enumerate(labels):
            Label(
                frame,
                text=lab,
                bg=self.color_content_bg,
                font=("Arial", 12)
            ).grid(row=i, column=0, padx=10, pady=7, sticky="w")

            ent = Entry(frame, width=30, font=("Arial", 12))
            ent.insert(0, values[i])

            if lab in ["Email", "Gender", "Role"]:
                ent.config(state="disabled")

            ent.grid(row=i, column=1, padx=10, pady=7)
            entries[lab] = ent

        def update():
            new_name = entries["Full Name"].get()
            new_phone = entries["Phone"].get()
            new_address = entries["Address"].get()

            if not new_name or not new_phone or not new_address:
                messagebox.showwarning("Warning", "All fields are required!")
                return

            try:
                self.service.update_profile(new_name, new_phone, new_address)
                self.user_full_name = new_name
                messagebox.showinfo("Success", "Profile updated successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update profile: {e}")

        Button(
            self.content,
            text="Save Changes",
            bg=self.color_accent,
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            command=update
        ).pack(pady=20)

    # ------------------ BOOK TAXI PAGE ------------------
    def show_book_taxi(self):
        self.clear_content()

        Label(
            self.content,
            text="Book a Taxi",
            font=("Arial", 18, "bold"),
            bg=self.color_content_bg
        ).pack(pady=20)

        frame = Frame(self.content, bg=self.color_content_bg)
        frame.pack(pady=10, padx=16, fill=X)

        label_opts = {"bg": self.color_content_bg, "anchor": "w", "font": ("Arial", 11), "width": 18}
        entry_pad = {"padx": 8, "pady": 5, "sticky": "w"}

        # --- load addresses from service ---
        try:
            self.districts = self.service.get_addresses()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load addresses: {e}")
            self.districts = []

        districts_with_default = ["Select Address"] + self.districts

        # ----- Pickup combobox (searchable) -----
        Label(frame, text="Pickup Location:", **label_opts) \
            .grid(row=0, column=0, **entry_pad)

        self.pickup_var = StringVar()
        self.pickup_combo = ttk.Combobox(
            frame,
            textvariable=self.pickup_var,
            values=districts_with_default,
            width=34
        )
        self.pickup_combo.grid(row=0, column=1, **entry_pad)
        self.pickup_combo.set("Select Address")

        def pickup_focus_in(event):
            if self.pickup_var.get() == "Select Address":
                self.pickup_combo.set("")
        self.pickup_combo.bind("<FocusIn>", pickup_focus_in)

        self.pickup_combo.bind(
            "<KeyRelease>",
            lambda e: self.update_combobox(self.pickup_combo, self.pickup_var)
        )

        # ----- Dropoff combobox (searchable) -----
        Label(frame, text="Dropoff Location:", **label_opts) \
            .grid(row=1, column=0, **entry_pad)

        self.drop_var = StringVar()
        self.drop_combo = ttk.Combobox(
            frame,
            textvariable=self.drop_var,
            values=districts_with_default,
            width=34
        )
        self.drop_combo.grid(row=1, column=1, **entry_pad)
        self.drop_combo.set("Select Address")

        def drop_focus_in(event):
            if self.drop_var.get() == "Select Address":
                self.drop_combo.set("")
        self.drop_combo.bind("<FocusIn>", drop_focus_in)

        self.drop_combo.bind(
            "<KeyRelease>",
            lambda e: self.update_combobox(self.drop_combo, self.drop_var)
        )

        # ----- Booking date (today + future only) -----
        Label(frame, text="Booking Date:", **label_opts) \
            .grid(row=2, column=0, **entry_pad)

        today = datetime.now().date()

        date_entry = DateEntry(
            frame,
            width=22,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            mindate=today
        )
        date_entry.set_date(today)
        date_entry.grid(row=2, column=1, **entry_pad)

        # ----- Booking time + NOW button -----
        Label(frame, text="Time (HH:MM):", **label_opts) \
            .grid(row=3, column=0, **entry_pad)

        time_container = Frame(frame, bg=self.color_content_bg)
        time_container.grid(row=3, column=1, **entry_pad)

        time_entry = Entry(time_container, width=18)
        time_entry.insert(0, datetime.now().strftime("%H:%M"))
        time_entry.pack(side=LEFT, padx=(0, 5))

        def set_current_time():
            now_str = datetime.now().strftime("%H:%M")
            time_entry.delete(0, END)
            time_entry.insert(0, now_str)

        ttk.Button(time_container, text="Now", command=set_current_time).pack(side=LEFT)

        # ---------------- Submit Booking ----------------
        def submit():
            if not self.customer_id:
                messagebox.showerror("Error", "Customer ID not available. Cannot create booking.")
                return

            pickup = self.pickup_var.get().strip()
            drop = self.drop_var.get().strip()
            booking_date_str = date_entry.get().strip()
            booking_time = time_entry.get().strip()

            # validate date (server-side)
            try:
                booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showwarning("Error", "Invalid date format.")
                return

            if not pickup or pickup == "Select Address":
                messagebox.showwarning("Error", "Please choose Pickup Location.")
                return
            if not drop or drop == "Select Address":
                messagebox.showwarning("Error", "Please choose Dropoff Location.")
                return
            if not booking_time:
                messagebox.showwarning("Error", "Please enter booking time.")
                return

            try:
                self.service.create_booking(pickup, drop, booking_date, booking_time)
                messagebox.showinfo("Stay Tuned", "Booking successful! Stay tuned for confirmation ✨")
                self.show_bookings()
            except ValueError as e:
                messagebox.showwarning("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create booking: {e}")
                print(f"[DEBUG] Booking insert failed: {e}")

        Button(
            self.content,
            text="Confirm Booking",
            bg="#16a34a",
            fg="white",
            width=20,
            height=2,
            command=submit
        ).pack(pady=20)

    def update_combobox(self, combo, var):
        """
        Filter combobox values based on typed input.
        Works with self.districts list.
        """
        if not hasattr(self, "districts"):
            return

        typed = var.get().strip().lower()

        if not typed:
            combo["values"] = ["Select Address"] + self.districts
            return

        filtered = [d for d in self.districts if typed in d.lower()]

        if not filtered:
            combo["values"] = ["Select Address"] + self.districts
        else:
            combo["values"] = filtered

    # ------------------ BOOKING HISTORY PAGE ------------------
    def show_bookings(self):
        self._current_page_method = self.show_bookings
        self.clear_content()

        Label(
            self.content,
            text="My Bookings",
            font=("Arial", 18, "bold"),
            bg=self.color_content_bg
        ).pack(pady=20)

        # Search / filter bar
        search_frame = Frame(self.content, bg=self.color_content_bg)
        search_frame.pack(fill=X, padx=20, pady=(0, 5))
        Label(search_frame, text="Search:", bg=self.color_content_bg, font=("Arial", 11)).pack(side=LEFT, padx=(0, 4))
        search_var = StringVar()
        search_entry = Entry(search_frame, textvariable=search_var, width=22)
        search_entry.pack(side=LEFT, padx=(0, 10))

        Label(search_frame, text="Status:", bg=self.color_content_bg, font=("Arial", 11)).pack(side=LEFT, padx=(0, 4))
        status_var = StringVar(value="All")
        status_cb = ttk.Combobox(
            search_frame,
            textvariable=status_var,
            values=["All", "Pending", "Accepted", "Completed", "Cancelled"],
            width=12,
            state="readonly",
        )
        status_cb.pack(side=LEFT, padx=(0, 10))

        columns = ("ID", "Pickup", "Dropoff", "Date", "Time", "Status", "Ride Start", "Ride Completion")
        table = ttk.Treeview(self.content, columns=columns, show="headings", height=15, style="Customer.Treeview")

        # striped rows
        table.tag_configure("evenrow", background=self.colors["treeview_even"])
        table.tag_configure("oddrow", background=self.colors["treeview_odd"])

        for col in columns:
            table.heading(col, text=col)
            if col == "ID":
                table.column(col, width=60, anchor=CENTER, stretch=False)
            elif col in ("Date", "Time", "Status"):
                table.column(col, width=100, anchor=CENTER, stretch=False)
            elif col in ("Ride Start", "Ride Completion"):
                table.column(col, width=140, anchor=CENTER, stretch=False)
            else:  # Pickup / Dropoff
                table.column(col, width=140, stretch=True)
        table.pack(fill=BOTH, padx=20, pady=10)

        # make sortable
        self._make_treeview_sortable(table, columns, numeric_cols={"ID"})

        if not self.customer_id:
            messagebox.showerror("Error", "Customer ID not available. Cannot load bookings.")
            return

        # load data
        self._customer_bookings_cache = []
        try:
            rows = self.service.get_bookings()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bookings: {e}")
            rows = []

        # Normalize rows to dict-like for easier filtering
        self._customer_bookings_cache = [
            {
                "ID": r[0],
                "Pickup": r[1],
                "Dropoff": r[2],
                "Date": r[3],
                "Time": r[4],
                "Status": r[5] if len(r) > 5 else "",
                "Ride Start": r[6] if len(r) > 6 else None,
                "Ride Completion": r[7] if len(r) > 7 else None,
            }
            for r in rows
        ]

        def _refresh_tree(filtered=None):
            for item in table.get_children():
                table.delete(item)
            data = filtered if filtered is not None else self._customer_bookings_cache
            for idx, r in enumerate(data):
                # Format timestamps for display
                ride_start = r.get("Ride Start")
                if ride_start:
                    if isinstance(ride_start, str):
                        ride_start_display = ride_start
                    else:
                        ride_start_display = ride_start.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    ride_start_display = "N/A"
                
                ride_completion = r.get("Ride Completion")
                if ride_completion:
                    if isinstance(ride_completion, str):
                        ride_completion_display = ride_completion
                    else:
                        ride_completion_display = ride_completion.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    ride_completion_display = "N/A"
                
                vals = [
                    r.get("ID"),
                    r.get("Pickup"),
                    r.get("Dropoff"),
                    r.get("Date"),
                    r.get("Time"),
                    r.get("Status"),
                    ride_start_display,
                    ride_completion_display,
                ]
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                table.insert("", END, values=vals, tags=(tag,))

        def _apply_filters(*_):
            text = (search_var.get() or "").strip().lower()
            status_filter = (status_var.get() or "All").strip().lower()

            filtered = []
            for r in self._customer_bookings_cache:
                # r dict with ID, Pickup, Dropoff, Date, Time, Status
                rid = r.get("ID")
                pickup = str(r.get("Pickup", ""))
                dropoff = str(r.get("Dropoff", ""))
                date_str = str(r.get("Date", ""))
                time_str = str(r.get("Time", ""))
                status_val = str(r.get("Status", ""))

                ride_start_str = str(r.get("Ride Start", ""))
                ride_completion_str = str(r.get("Ride Completion", ""))
                
                if text:
                    combined = " ".join(
                        [str(rid), pickup, dropoff, date_str, time_str, status_val, ride_start_str, ride_completion_str]
                    ).lower()
                    if text not in combined:
                        continue

                if status_filter and status_filter != "all":
                    if status_val.lower() != status_filter:
                        continue

                filtered.append(r)

            _refresh_tree(filtered)

        search_entry.bind("<KeyRelease>", _apply_filters)
        status_cb.bind("<<ComboboxSelected>>", _apply_filters)
        _refresh_tree()

        def cancel():
            selected = table.selection()
            if not selected:
                messagebox.showwarning("Error", "Select a booking!")
                return

            booking_id = table.item(selected[0])['values'][0]

            try:
                self.service.cancel_booking(booking_id)
                messagebox.showinfo("Success", "Booking cancelled!")
                self.show_bookings()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel booking: {e}")

        Button(
            self.content,
            text="Cancel Booking",
            bg="#ef4444",
            fg="white",
            width=20,
            height=2,
            command=cancel
        ).pack(pady=10)

    # ------------------ SETTINGS & SUPPORT ------------------
    def show_settings(self):
        self.clear_content()
        Label(
            self.content,
            text="Settings",
            font=("Arial", 18, "bold"),
            bg=self.color_content_bg
        ).pack(pady=20)

        frame = Frame(self.content, bg=self.color_content_bg)
        frame.pack(pady=10)

        Label(
            frame,
            text="Notification Preferences",
            bg=self.color_content_bg,
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.email_notif_var = BooleanVar(value=True)
        self.sms_notif_var = BooleanVar(value=True)

        Checkbutton(
            frame,
            text="Email notifications",
            variable=self.email_notif_var,
            bg=self.color_content_bg
        ).grid(row=1, column=0, sticky="w", padx=20)
        Checkbutton(
            frame,
            text="SMS notifications",
            variable=self.sms_notif_var,
            bg=self.color_content_bg
        ).grid(row=2, column=0, sticky="w", padx=20)

        Label(
            frame,
            text="(These settings are placeholders – connect them to DB later.)",
            bg=self.color_content_bg,
            fg="#6b7280"
        ).grid(row=3, column=0, sticky="w", padx=10, pady=10)

    def show_support(self):
        self.clear_content()

        Label(
            self.content,
            text="Support",
            font=("Arial", 18, "bold"),
            bg=self.color_content_bg
        ).pack(pady=20)

        Label(
            self.content,
            text="If you face any issue with your bookings or profile,\n"
                 "you can contact our support team.",
            font=("Arial", 12),
            bg=self.color_content_bg,
            justify="center"
        ).pack(pady=10)

        def contact_support():
            messagebox.showinfo(
                "Contact Support",
                "You can contact support at: support@example.com\n"
                "Or call: +977-XXXXXXXXXX"
            )

        Button(
            self.content,
            text="Contact Support",
            bg=self.color_accent,
            fg="white",
            width=20,
            height=2,
            command=contact_support
        ).pack(pady=20)

    # ------------------ MISC & LOGOUT ------------------
    def doNothing(self):
        messagebox.showinfo("Coming Soon", "Feature not implemented yet ✨")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            if self.logout_callback:
                try:
                    self.logout_callback()
                except Exception as e:
                    print(f"[DEBUG] logout_callback failed: {e}")
            else:
                self.root.destroy()

    # ------------------ DESTROY / CLEANUP ------------------
    def destroy(self):
        """Remove dashboard UI when logging out / switching user."""
        try:
            self.sidebar.destroy()
        except Exception:
            pass
        try:
            self.content.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    root = Tk()
    CustomerDashboard(root, customer_id=1)
    root.mainloop()
