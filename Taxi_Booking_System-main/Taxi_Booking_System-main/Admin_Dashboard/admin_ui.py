from tkinter import *
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime
import os
from Admin_Dashboard.admin_service import AdminService
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme_manager import get_theme_colors, save_theme_preference, get_theme_preference


class AdminDashboard:
    def __init__(self, root, admin_id, logout_callback=None):
        self.root = root
        self.admin_id = admin_id
        self.logout_callback = logout_callback

        # Initialize service layer
        self.service = AdminService(admin_id)
        
        # Load photo path from profile
        try:
            profile = self.service.get_profile()
            self.photo_path = profile[6] if profile and len(profile) > 6 else None
        except Exception:
            self.photo_path = None

        # Cache for image reference
        self.profile_img_tk = None

        # Initialize theme
        self.current_theme = get_theme_preference()
        self.colors = get_theme_colors(self.current_theme)
        self._update_color_vars()

        # window
        try:
            self.root.title("Admin Dashboard")
            self.root.geometry("1100x650")
        except Exception:
            pass
        self.root.configure(bg=self.color_content_bg)

        # Apply theme to treeview styles
        self._apply_treeview_theme()

        # ------------- MENU BAR -------------
        self.mainmenu = Menu(self.root)

        filemenu = Menu(self.mainmenu, tearoff=0)
        filemenu.add_command(label='New', command=self._do_nothing)
        filemenu.add_command(label='Open', command=self._do_nothing)
        filemenu.add_command(label='Save', command=self._do_nothing)
        filemenu.add_command(label='Save as...', command=self._do_nothing)
        filemenu.add_command(label='Close', command=self._do_nothing)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.root.quit)
        self.mainmenu.add_cascade(label='File', menu=filemenu)

        editmenu = Menu(self.mainmenu, tearoff=0)
        editmenu.add_command(label='Undo', command=self._do_nothing)
        editmenu.add_command(label='Redo', command=self._do_nothing)
        editmenu.add_separator()
        editmenu.add_command(label='Cut', command=self._do_nothing)
        editmenu.add_command(label='Copy', command=self._do_nothing)
        editmenu.add_command(label='Paste', command=self._do_nothing)
        self.mainmenu.add_cascade(label='Edit', menu=editmenu)

        viewmenu = Menu(self.mainmenu, tearoff=0)
        viewmenu.add_command(label='Home', command=self.show_home)
        viewmenu.add_command(label='All Bookings', command=self.show_all_bookings)
        viewmenu.add_command(label='Customers', command=self.show_customers)
        viewmenu.add_command(label='Assign Driver', command=self.show_assign_driver)
        viewmenu.add_command(label='Create Booking', command=self.show_create_booking)
        viewmenu.add_command(label='Create Driver', command=self.show_create_driver)
        viewmenu.add_command(label='Profile', command=self.show_profile)
        self.mainmenu.add_cascade(label='View', menu=viewmenu)

        toolsmenu = Menu(self.mainmenu, tearoff=0)
        toolsmenu.add_command(label='Settings', command=self.show_settings)
        toolsmenu.add_command(label='Support', command=self.show_support)
        toolsmenu.add_command(label='Export Data', command=self._do_nothing)
        self.mainmenu.add_cascade(label='Tools', menu=toolsmenu)

        helpmenu = Menu(self.mainmenu, tearoff=0)
        helpmenu.add_command(label='User Guide', command=self._do_nothing)
        helpmenu.add_command(label='About', command=self._do_nothing)
        helpmenu.add_command(label='Contact Support', command=self._show_support_popup)
        self.mainmenu.add_cascade(label='Help', menu=helpmenu)

        self.root.config(menu=self.mainmenu)

        # ------------- MAIN LAYOUT -------------
        self.sidebar = Frame(self.root, bg=self.color_sidebar_bg, width=240)
        self.sidebar.pack(side=LEFT, fill=Y)

        self.content = Frame(self.root, bg=self.color_content_bg)
        self.content.pack(side=RIGHT, fill=BOTH, expand=True)

        self._build_sidebar()

        # Track current page for theme refresh
        self._current_page_method = self.show_home
        
        # start
        self.show_home()

    # ---------------- UI helpers ----------------
    def _build_sidebar(self):
        Label(
            self.sidebar,
            text="Admin Menu",
            fg="white",
            bg=self.color_sidebar_bg,
            font=("Arial", 16, "bold"),
            pady=20
        ).pack()

        btns = [
            ("Home", self.show_home),
            ("View All Bookings", self.show_all_bookings),
            ("Assign Driver", self.show_assign_driver),
            ("View Customers", self.show_customers),
            ("Create Booking", self.show_create_booking),
            ("Create Driver", self.show_create_driver),
            ("Profile", self.show_profile),
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
            width=20,
            bg="#ef4444",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self._on_logout
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
        self.color_entry_bg = self.colors["entry_bg"]
        self.color_entry_fg = self.colors["entry_fg"]

    def _apply_treeview_theme(self):
        """Apply theme to treeview styles."""
        try:
            style = ttk.Style(self.root)
            style.configure(
                "Admin.Treeview",
                rowheight=22,
                padding=(2, 1),
                borderwidth=1,
                background=self.colors["treeview_bg"],
                foreground=self.colors["treeview_fg"],
                fieldbackground=self.colors["treeview_bg"]
            )
            style.configure(
                "Admin.Treeview.Heading",
                padding=(4, 2),
                borderwidth=1,
                background=self.colors["sidebar_btn"],
                foreground="white"
            )
            style.map(
                "Admin.Treeview",
                background=[("selected", self.colors["treeview_selected_bg"])],
                foreground=[("selected", self.colors["treeview_selected_fg"])]
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
            self.show_home()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ------------- Treeview helpers -------------
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

    # ---------------- Home ----------------
    def show_home(self):
        self._current_page_method = self.show_home
        self.clear_content()
        
        # Hero Section
        hero_frame = Frame(self.content, bg=self.color_content_bg)
        hero_frame.pack(pady=(20, 30))
        
        Label(
            hero_frame,
            text="Welcome to Admin Dashboard",
            font=("Arial", 28, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack()
        
        Label(
            hero_frame,
            text="Manage your taxi booking system efficiently",
            font=("Arial", 12),
            bg=self.color_content_bg,
            fg=self.color_text_secondary
        ).pack(pady=(5, 0))

        # Stats Cards Container
        stats_container = Frame(self.content, bg=self.color_content_bg)
        stats_container.pack(pady=20, padx=20, fill=X)

        try:
            stats = self.service.get_stats()
            total_customers = stats.get("customers", 0)
            total_drivers = stats.get("drivers", 0)
            total_bookings = stats.get("bookings", 0)
        except Exception as e:
            total_customers = total_drivers = total_bookings = 0

        # Stat Card 1: Customers
        card1 = Frame(stats_container, bg=self.color_card_bg, relief="flat", bd=1)
        card1.pack(side=LEFT, padx=10, fill=BOTH, expand=True)
        card1_inner = Frame(card1, bg=self.color_card_bg)
        card1_inner.pack(padx=20, pady=20, fill=BOTH)
        Label(card1_inner, text="👥", font=("Arial", 32), bg=self.color_card_bg).pack()
        Label(card1_inner, text=str(total_customers), font=("Arial", 32, "bold"), bg=self.color_card_bg, fg="#2563eb").pack()
        Label(card1_inner, text="Customers", font=("Arial", 12), bg=self.color_card_bg, fg=self.color_card_text_secondary).pack()

        # Stat Card 2: Drivers
        card2 = Frame(stats_container, bg=self.color_card_bg, relief="flat", bd=1)
        card2.pack(side=LEFT, padx=10, fill=BOTH, expand=True)
        card2_inner = Frame(card2, bg=self.color_card_bg)
        card2_inner.pack(padx=20, pady=20, fill=BOTH)
        Label(card2_inner, text="🚗", font=("Arial", 32), bg=self.color_card_bg).pack()
        Label(card2_inner, text=str(total_drivers), font=("Arial", 32, "bold"), bg=self.color_card_bg, fg="#16a34a").pack()
        Label(card2_inner, text="Drivers", font=("Arial", 12), bg=self.color_card_bg, fg=self.color_card_text_secondary).pack()

        # Stat Card 3: Bookings
        card3 = Frame(stats_container, bg=self.color_card_bg, relief="flat", bd=1)
        card3.pack(side=LEFT, padx=10, fill=BOTH, expand=True)
        card3_inner = Frame(card3, bg=self.color_card_bg)
        card3_inner.pack(padx=20, pady=20, fill=BOTH)
        Label(card3_inner, text="📋", font=("Arial", 32), bg=self.color_card_bg).pack()
        Label(card3_inner, text=str(total_bookings), font=("Arial", 32, "bold"), bg=self.color_card_bg, fg="#dc2626").pack()
        Label(card3_inner, text="Total Bookings", font=("Arial", 12), bg=self.color_card_bg, fg=self.color_card_text_secondary).pack()

        # Note: Quick booking section removed per request

    # ---------------- All bookings ----------------
    def show_all_bookings(self):
        self._current_page_method = self.show_all_bookings
        self.clear_content()
        Label(
            self.content,
            text="All Bookings",
            font=("Arial", 20, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=10)

        # Search / filter bar
        search_frame = Frame(self.content, bg=self.color_content_bg)
        search_frame.pack(fill=X, padx=10, pady=(0, 5))

        Label(search_frame, text="Search:", bg=self.color_content_bg, font=("Arial", 11)).pack(side=LEFT, padx=(0, 4))
        search_var = StringVar()
        search_entry = Entry(search_frame, textvariable=search_var, width=22)
        search_entry.pack(side=LEFT, padx=(0, 10))

        # Status filter
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

        # Customer filter
        Label(search_frame, text="Customer:", bg=self.color_content_bg, font=("Arial", 11)).pack(side=LEFT, padx=(0, 4))
        customer_var = StringVar()
        customer_entry = Entry(search_frame, textvariable=customer_var, width=16)
        customer_entry.pack(side=LEFT, padx=(0, 10))

        # Driver filter
        Label(search_frame, text="Driver:", bg=self.color_content_bg, font=("Arial", 11)).pack(side=LEFT, padx=(0, 4))
        driver_var = StringVar()
        driver_entry = Entry(search_frame, textvariable=driver_var, width=16)
        driver_entry.pack(side=LEFT, padx=(0, 10))

        frame = Frame(self.content, bg=self.color_content_bg)
        frame.pack(fill=BOTH, expand=True, pady=10, padx=10)

        cols = ("ID", "Customer", "Pickup", "Dropoff", "Date", "Time", "Status", "Driver", "Ride Start", "Ride Completion")
        self.bookings_tree = ttk.Treeview(frame, columns=cols, show="headings", height=18, style="Admin.Treeview")
        # row stripe tags
        self.bookings_tree.tag_configure("evenrow", background=self.colors["treeview_even"])
        self.bookings_tree.tag_configure("oddrow", background=self.colors["treeview_odd"])
        for c in cols:
            self.bookings_tree.heading(c, text=c)
            if c == "ID":
                self.bookings_tree.column(c, width=55, anchor=CENTER, stretch=False)
            elif c in ("Date", "Time"):
                self.bookings_tree.column(c, width=80, anchor=CENTER, stretch=False)
            elif c == "Status":
                self.bookings_tree.column(c, width=90, anchor=CENTER, stretch=False)
            elif c in ("Ride Start", "Ride Completion"):
                self.bookings_tree.column(c, width=140, anchor=CENTER, stretch=False)
            elif c == "Customer":
                self.bookings_tree.column(c, width=120, stretch=True)
            elif c == "Driver":
                self.bookings_tree.column(c, width=100, stretch=True)
            elif c == "Pickup":
                self.bookings_tree.column(c, width=120, stretch=True)
            elif c == "Dropoff":
                self.bookings_tree.column(c, width=120, stretch=True)
        self.bookings_tree.pack(fill=BOTH, expand=True, side=LEFT)

        scroll = ttk.Scrollbar(frame, orient=VERTICAL, command=self.bookings_tree.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.bookings_tree.configure(yscrollcommand=scroll.set)

        # Make sortable
        self._make_treeview_sortable(self.bookings_tree, cols, numeric_cols={"ID"})

        btn_frame = Frame(self.content, bg=self.color_content_bg)
        btn_frame.pack(pady=8)
        Button(btn_frame, text="Refresh", width=12, command=self.show_all_bookings).pack(side=LEFT, padx=6)
        Button(btn_frame, text="Cancel Booking", bg="#ef4444", fg="white", width=15,
               command=self.cancel_selected_booking).pack(side=LEFT, padx=6)

        # Load data
        self._all_bookings_cache = []
        try:
            bookings = self.service.get_all_bookings()
            self._all_bookings_cache = bookings or []
        except Exception as e:
            messagebox.showerror("Error", str(e))

        def _refresh_tree(filtered=None):
            for item in self.bookings_tree.get_children():
                self.bookings_tree.delete(item)
            data = filtered if filtered is not None else self._all_bookings_cache
            for idx, b in enumerate(data):
                # Format timestamps for display
                ride_start = b.get("ride_start_timestamp")
                if ride_start:
                    if isinstance(ride_start, str):
                        ride_start_display = ride_start
                    else:
                        ride_start_display = ride_start.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    ride_start_display = "N/A"
                
                ride_completion = b.get("ride_completion_timestamp")
                if ride_completion:
                    if isinstance(ride_completion, str):
                        ride_completion_display = ride_completion
                    else:
                        ride_completion_display = ride_completion.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    ride_completion_display = "N/A"
                
                vals = [
                    b.get("id"),
                    b.get("customer"),
                    b.get("pickup"),
                    b.get("dropoff"),
                    b.get("date"),
                    b.get("time"),
                    b.get("status"),
                    b.get("driver"),
                    ride_start_display,
                    ride_completion_display,
                ]
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.bookings_tree.insert("", END, values=vals, tags=(tag,))

        def _apply_filters(*_):
            text = (search_var.get() or "").strip().lower()
            status_filter = (status_var.get() or "All").strip().lower()
            cust_filter = (customer_var.get() or "").strip().lower()
            driver_filter = (driver_var.get() or "").strip().lower()

            filtered = []
            for b in self._all_bookings_cache:
                # base values
                bid = b.get("id")
                customer = str(b.get("customer", ""))
                pickup = str(b.get("pickup", ""))
                dropoff = str(b.get("dropoff", ""))
                date_str = str(b.get("date", ""))
                time_str = str(b.get("time", ""))
                status = str(b.get("status", ""))
                driver = str(b.get("driver", ""))

                # free-text search across all fields
                if text:
                    combined = " ".join(
                        [str(bid), customer, pickup, dropoff, date_str, time_str, status, driver]
                    ).lower()
                    if text not in combined:
                        continue

                # status filter (except "All")
                if status_filter and status_filter != "all":
                    if status.lower() != status_filter:
                        continue

                # customer filter (substring)
                if cust_filter and cust_filter not in customer.lower():
                    continue

                # driver filter (substring)
                if driver_filter and driver_filter not in driver.lower():
                    continue

                filtered.append(b)

            _refresh_tree(filtered)

        # Bind filters
        search_entry.bind("<KeyRelease>", _apply_filters)
        customer_entry.bind("<KeyRelease>", _apply_filters)
        driver_entry.bind("<KeyRelease>", _apply_filters)
        status_cb.bind("<<ComboboxSelected>>", _apply_filters)

        _refresh_tree()

    def cancel_selected_booking(self):
        sel = self.bookings_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a booking to cancel.")
            return
        booking_id = self.bookings_tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirm", f"Cancel booking {booking_id}?"):
            return
        try:
            self.service.cancel_booking(booking_id)
            messagebox.showinfo("Success", "Booking cancelled.")
            self.show_all_bookings()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- Assign driver ----------------
    def show_assign_driver(self):
        self.clear_content()
        Label(
            self.content,
            text="Assign Driver",
            font=("Arial", 20, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=10)

        frame = Frame(self.content, bg=self.color_content_bg)
        frame.pack(pady=20, padx=16, fill=X)

        label_opts = {"bg": self.color_content_bg, "anchor": "w", "font": ("Arial", 11), "width": 16}
        entry_pad = {"padx": 8, "pady": 6, "sticky": "w"}

        Label(frame, text="Booking ID:", **label_opts).grid(row=0, column=0, **entry_pad)
        booking_id_entry = Entry(frame, width=24)
        booking_id_entry.grid(row=0, column=1, **entry_pad)

        Label(frame, text="Driver:", **label_opts).grid(row=1, column=0, **entry_pad)
        driver_cb = ttk.Combobox(frame, width=52, state="readonly")
        driver_cb.grid(row=1, column=1, **entry_pad)
        Label(frame, text="Booking ID:", **label_opts).grid(row=0, column=0, **entry_pad)
        booking_id_entry = Entry(frame, width=24)
        booking_id_entry.grid(row=0, column=1, **entry_pad)

        Label(frame, text="Driver:", **label_opts).grid(row=1, column=0, **entry_pad)
        driver_cb = ttk.Combobox(frame, width=52, state="readonly")
        driver_cb.grid(row=1, column=1, **entry_pad)
        driver_cb._value_map = {}

        def load_driver_options():
            try:
                options, value_map = self.service.get_drivers_for_assignment()
                driver_cb["values"] = options
                driver_cb._value_map = value_map
            except Exception as e:
                messagebox.showerror("Error", str(e))

        load_driver_options()
        Button(frame, text="Refresh Drivers", command=load_driver_options).grid(row=1, column=2, padx=8)

        def assign():
            disp = driver_cb.get()
            bid = booking_id_entry.get().strip()
            if not bid:
                return messagebox.showwarning("Error", "Enter booking id.")
            if not disp:
                return messagebox.showwarning("Error", "Select driver.")
            try:
                booking_id = int(bid)
            except:
                return messagebox.showwarning("Error", "Invalid booking id.")
            sel = driver_cb._value_map.get(disp)
            if not sel:
                return messagebox.showwarning("Error", "Invalid driver selected.")
            source, ident = sel

            try:
                self.service.assign_driver(booking_id, source, ident)
                messagebox.showinfo("Success", "Driver assigned successfully.")
                booking_id_entry.delete(0, END)
                driver_cb.set("")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(frame, text="Assign", width=20, bg="#0a84ff", fg="white", command=assign).grid(row=2, column=1, pady=14)

    # ---------------- View / Manage customers ----------------
    def show_customers(self):
        self.clear_content()
        Label(
            self.content,
            text="Customers & Users",
            font=("Arial", 20, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=10)

        # Search / filters
        search_frame = Frame(self.content, bg=self.color_content_bg)
        search_frame.pack(fill=X, padx=10, pady=(0, 5))
        Label(search_frame, text="Search:", bg=self.color_content_bg, font=("Arial", 11)).pack(side=LEFT, padx=(0, 4))
        search_var = StringVar()
        search_entry = Entry(search_frame, textvariable=search_var, width=22)
        search_entry.pack(side=LEFT, padx=(0, 10))

        Label(search_frame, text="Role:", bg=self.color_content_bg, font=("Arial", 11)).pack(side=LEFT, padx=(0, 4))
        role_var = StringVar(value="All")
        role_cb = ttk.Combobox(
            search_frame,
            textvariable=role_var,
            values=["All", "Admin", "Customer", "Driver"],
            width=12,
            state="readonly",
        )
        role_cb.pack(side=LEFT, padx=(0, 10))

        Label(search_frame, text="Phone:", bg=self.color_content_bg, font=("Arial", 11)).pack(side=LEFT, padx=(0, 4))
        phone_var = StringVar()
        phone_entry = Entry(search_frame, textvariable=phone_var, width=16)
        phone_entry.pack(side=LEFT, padx=(0, 10))

        frame = Frame(self.content, bg=self.color_content_bg)
        frame.pack(fill=BOTH, expand=True, pady=10, padx=10)

        cols = ("ID", "Name", "Email", "Phone", "Address", "Role")
        self.customers_tree = ttk.Treeview(frame, columns=cols, show="headings", height=18, style="Admin.Treeview")
        # row stripe tags
        self.customers_tree.tag_configure("evenrow", background="#ffffff")
        self.customers_tree.tag_configure("oddrow", background="#f3f4f6")
        for c in cols:
            self.customers_tree.heading(c, text=c)
            if c == "ID":
                self.customers_tree.column(c, width=55, anchor=CENTER, stretch=False)
            elif c == "Name":
                self.customers_tree.column(c, width=130, stretch=True)
            elif c == "Email":
                self.customers_tree.column(c, width=190, stretch=True)
            elif c == "Phone":
                self.customers_tree.column(c, width=105, anchor=CENTER, stretch=False)
            elif c == "Role":
                self.customers_tree.column(c, width=70, anchor=CENTER, stretch=False)
            else:  # Address
                self.customers_tree.column(c, width=190, stretch=True)
        self.customers_tree.pack(fill=BOTH, expand=True, side=LEFT)

        scroll = ttk.Scrollbar(frame, orient=VERTICAL, command=self.customers_tree.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.customers_tree.configure(yscrollcommand=scroll.set)

        # Make sortable
        self._make_treeview_sortable(self.customers_tree, cols, numeric_cols={"ID"})

        btn_frame = Frame(self.content, bg=self.color_content_bg)
        btn_frame.pack(pady=8)
        Button(btn_frame, text="Refresh", width=12, command=self.show_customers).pack(side=LEFT, padx=6)
        Button(btn_frame, text="Edit", width=12, bg=self.color_accent, fg="white",
               command=self.edit_selected_customer).pack(side=LEFT, padx=6)
        Button(btn_frame, text="Delete", width=12, bg="#ef4444", fg="white",
               command=self.delete_selected_customer).pack(side=LEFT, padx=6)

        self._all_customers_cache = []
        try:
            rows = self.service.get_all_users()
            self._all_customers_cache = rows or []
        except Exception as e:
            messagebox.showerror("Error", str(e))

        def _refresh_tree(filtered=None):
            for item in self.customers_tree.get_children():
                self.customers_tree.delete(item)
            data = filtered if filtered is not None else self._all_customers_cache
            for idx, r in enumerate(data):
                vals = list(r)
                while len(vals) < 6:
                    vals.append("")
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.customers_tree.insert("", END, values=vals[:6], tags=(tag,))

        def _apply_filters(*_):
            text = (search_var.get() or "").strip().lower()
            role = (role_var.get() or "All").strip().lower()
            phone = (phone_var.get() or "").strip().lower()

            filtered = []
            for r in self._all_customers_cache:
                # r: (id, name, email, phone, address, role)
                rid = r[0] if len(r) > 0 else ""
                name = r[1] if len(r) > 1 else ""
                email = r[2] if len(r) > 2 else ""
                phone_val = r[3] if len(r) > 3 else ""
                address = r[4] if len(r) > 4 else ""
                role_val = r[5] if len(r) > 5 else ""

                if text:
                    combined = " ".join(str(v) for v in (rid, name, email, phone_val, address, role_val)).lower()
                    if text not in combined:
                        continue

                if role and role != "all":
                    if str(role_val).lower() != role:
                        continue

                if phone and phone not in str(phone_val).lower():
                    continue

                filtered.append(r)

            _refresh_tree(filtered)

        search_entry.bind("<KeyRelease>", _apply_filters)
        phone_entry.bind("<KeyRelease>", _apply_filters)
        role_cb.bind("<<ComboboxSelected>>", _apply_filters)

        _refresh_tree()

    def edit_selected_customer(self):
        sel = self.customers_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a customer to edit.")
            return
        customer_id = self.customers_tree.item(sel[0])["values"][0]
        self.edit_customer_form(customer_id, refresh_func=self.show_customers)

    def edit_customer_form(self, customer_id, refresh_func=None):
        try:
            row = self.service.get_user(customer_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        if not row:
            messagebox.showerror("Error", "Customer not found.")
            return

        form = Toplevel(self.root)
        form.title("Edit User")
        fields = ["Full Name", "Email", "Phone", "Address", "Role"]
        entries = {}
        for i, f in enumerate(fields):
            Label(form, text=f).grid(row=i, column=0, padx=10, pady=6, sticky=E)
            ent = Entry(form, width=40)
            ent.grid(row=i, column=1, padx=10, pady=6)
            entries[f] = ent
        ent_vals = [row[1], row[2], row[3], row[4], row[5]]
        for i, v in enumerate(ent_vals):
            entries[fields[i]].insert(0, v if v is not None else "")
            if fields[i] == "Email":
                entries[fields[i]].config(state="disabled")

        def save():
            new_name = entries["Full Name"].get().strip()
            new_phone = entries["Phone"].get().strip()
            new_address = entries["Address"].get().strip()
            new_role = entries["Role"].get().strip() or "Customer"
            try:
                self.service.update_user(customer_id, new_name, new_phone, new_address, new_role)
                messagebox.showinfo("Success", "User updated.")
                form.destroy()
                if refresh_func:
                    refresh_func()
            except ValueError as e:
                messagebox.showwarning("Validation", str(e))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(form, text="Save", bg="#16a34a", fg="white", command=save).grid(
            row=len(fields), column=0, columnspan=2, pady=12
        )

    def delete_selected_customer(self):
        sel = self.customers_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a customer to delete.")
            return
        customer_id = self.customers_tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirm", f"Delete user {customer_id}?"):
            return
        try:
            self.service.delete_user(customer_id)
            messagebox.showinfo("Success", "User deleted.")
            self.show_customers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- Create booking (admin) ----------------
    def show_create_booking(self):
        self._current_page_method = self.show_create_booking
        self.clear_content()
        Label(
            self.content,
            text="Create Booking (On Behalf of Customer)",
            font=("Arial", 18, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=10)

        frame = Frame(self.content, bg=self.color_content_bg)
        frame.pack(pady=10, padx=16, fill=X)

        label_opts = {"bg": self.color_content_bg, "anchor": "w", "font": ("Arial", 11), "width": 18}
        entry_pad = {"padx": 8, "pady": 5, "sticky": "w"}

        # Customer selection
        Label(frame, text="Customer:", **label_opts).grid(row=0, column=0, **entry_pad)
        customer_cb = ttk.Combobox(frame, width=46, state="readonly")
        customer_cb.grid(row=0, column=1, **entry_pad)

        try:
            customers = self.service.get_customers_for_booking()
            options = [f"{c[0]} - {c[1]} ({c[2]})" for c in customers]
            customer_cb["values"] = options
            customer_map = {options[i]: customers[i][0] for i in range(len(options))}
        except Exception as e:
            messagebox.showerror("Error", str(e))
            customer_map = {}

        # Load addresses from service
        try:
            districts = self.service.get_addresses()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load addresses: {e}")
            districts = []

        districts_with_default = ["Select Address"] + districts

        # Pickup combobox (searchable)
        Label(frame, text="Pickup Location:", **label_opts).grid(row=1, column=0, **entry_pad)
        pickup_var = StringVar()
        pickup_combo = ttk.Combobox(
            frame,
            textvariable=pickup_var,
            values=districts_with_default,
            width=43
        )
        pickup_combo.grid(row=1, column=1, **entry_pad)
        pickup_combo.set("Select Address")

        def pickup_focus_in(event):
            if pickup_var.get() == "Select Address":
                pickup_combo.set("")
        pickup_combo.bind("<FocusIn>", pickup_focus_in)

        def update_pickup_combobox(event):
            typed = pickup_var.get().strip().lower()
            if not typed:
                pickup_combo["values"] = districts_with_default
                return
            filtered = [d for d in districts if typed in d.lower()]
            if not filtered:
                pickup_combo["values"] = districts_with_default
            else:
                pickup_combo["values"] = filtered

        pickup_combo.bind("<KeyRelease>", update_pickup_combobox)

        # Dropoff combobox (searchable)
        Label(frame, text="Dropoff Location:", **label_opts).grid(row=2, column=0, **entry_pad)
        drop_var = StringVar()
        drop_combo = ttk.Combobox(
            frame,
            textvariable=drop_var,
            values=districts_with_default,
            width=43
        )
        drop_combo.grid(row=2, column=1, **entry_pad)
        drop_combo.set("Select Address")

        def drop_focus_in(event):
            if drop_var.get() == "Select Address":
                drop_combo.set("")
        drop_combo.bind("<FocusIn>", drop_focus_in)

        def update_drop_combobox(event):
            typed = drop_var.get().strip().lower()
            if not typed:
                drop_combo["values"] = districts_with_default
                return
            filtered = [d for d in districts if typed in d.lower()]
            if not filtered:
                drop_combo["values"] = districts_with_default
            else:
                drop_combo["values"] = filtered

        drop_combo.bind("<KeyRelease>", update_drop_combobox)

        # Booking date (DateEntry widget)
        Label(frame, text="Booking Date:", **label_opts).grid(row=3, column=0, **entry_pad)
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
        date_entry.grid(row=3, column=1, **entry_pad)

        # Booking time + NOW button
        Label(frame, text="Time (HH:MM):", **label_opts).grid(row=4, column=0, **entry_pad)
        time_container = Frame(frame, bg=self.color_content_bg)
        time_container.grid(row=4, column=1, **entry_pad)
        time_entry = Entry(time_container, width=18)
        time_entry.insert(0, datetime.now().strftime("%H:%M"))
        time_entry.pack(side=LEFT, padx=(0, 5))

        def set_current_time():
            now_str = datetime.now().strftime("%H:%M")
            time_entry.delete(0, END)
            time_entry.insert(0, now_str)

        ttk.Button(time_container, text="Now", command=set_current_time).pack(side=LEFT)

        # Taxi Type (optional)
        Label(frame, text="Taxi Type (optional):", **label_opts).grid(row=5, column=0, **entry_pad)
        taxi_ent = Entry(frame, width=43)
        taxi_ent.grid(row=5, column=1, **entry_pad)

        def submit_booking():
            sel = customer_cb.get()
            if not sel:
                return messagebox.showwarning("Error", "Please select a customer.")
            
            customer_id = customer_map.get(sel)
            if not customer_id:
                return messagebox.showwarning("Error", "Invalid customer selection.")
            
            pickup = pickup_var.get().strip()
            dropoff = drop_var.get().strip()
            booking_date_str = date_entry.get().strip()
            booking_time = time_entry.get().strip()
            taxi_type = taxi_ent.get().strip() or None

            # Validate date
            try:
                booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
            except ValueError:
                return messagebox.showwarning("Error", "Invalid date format.")

            # Validate fields
            if not pickup or pickup == "Select Address":
                return messagebox.showwarning("Error", "Please choose Pickup Location.")
            if not dropoff or dropoff == "Select Address":
                return messagebox.showwarning("Error", "Please choose Dropoff Location.")
            if not booking_time:
                return messagebox.showwarning("Error", "Please enter booking time.")

            try:
                self.service.create_booking(customer_id, pickup, dropoff, booking_date_str, booking_time, taxi_type)
                messagebox.showinfo("Success", "Booking created successfully! ✨")
                # Reset form
                customer_cb.set("")
                pickup_combo.set("Select Address")
                drop_combo.set("Select Address")
                date_entry.set_date(today)
                time_entry.delete(0, END)
                time_entry.insert(0, datetime.now().strftime("%H:%M"))
                taxi_ent.delete(0, END)
            except ValueError as e:
                messagebox.showwarning("Validation", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create booking: {e}")

        Button(
            self.content,
            text="Create Booking",
            bg="#16a34a",
            fg="white",
            width=20,
            height=2,
            command=submit_booking
        ).pack(pady=14)

    # ---------------- Create Driver ----------------
    def show_create_driver(self):
        self.clear_content()
        Label(
            self.content,
            text="Create Driver",
            font=("Arial", 18, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=10)

        frame = Frame(self.content, bg=self.color_content_bg)
        frame.pack(pady=10, padx=16, fill=X)

        label_opts = {"bg": self.color_content_bg, "anchor": "w", "font": ("Arial", 11), "width": 18}
        entry_pad = {"padx": 8, "pady": 6, "sticky": "w"}

        Label(frame, text="Full Name:", **label_opts).grid(row=0, column=0, **entry_pad)
        name_ent = Entry(frame, width=44)
        name_ent.grid(row=0, column=1, **entry_pad)

        Label(frame, text="Email:", **label_opts).grid(row=1, column=0, **entry_pad)
        email_ent = Entry(frame, width=44)
        email_ent.grid(row=1, column=1, **entry_pad)

        Label(frame, text="Phone:", **label_opts).grid(row=2, column=0, **entry_pad)
        phone_ent = Entry(frame, width=44)
        phone_ent.grid(row=2, column=1, **entry_pad)

        Label(frame, text="License Num:", **label_opts).grid(row=3, column=0, **entry_pad)
        lic_ent = Entry(frame, width=44)
        lic_ent.grid(row=3, column=1, **entry_pad)

        Label(frame, text="Registration Num:", **label_opts).grid(row=4, column=0, **entry_pad)
        reg_ent = Entry(frame, width=44)
        reg_ent.grid(row=4, column=1, **entry_pad)

        Label(frame, text="Password:", **label_opts).grid(row=5, column=0, **entry_pad)
        pass_ent = Entry(frame, width=44, show="*")
        pass_ent.grid(row=5, column=1, **entry_pad)

        def submit_driver():
            name = name_ent.get().strip()
            email = email_ent.get().strip()
            phone = phone_ent.get().strip()
            lic = lic_ent.get().strip()
            reg = reg_ent.get().strip()
            pwd = pass_ent.get().strip()
            try:
                self.service.create_or_update_driver(name, email, phone, lic, reg, pwd)
                messagebox.showinfo("Success", "Driver created/updated.")
                name_ent.delete(0, END)
                email_ent.delete(0, END)
                phone_ent.delete(0, END)
                lic_ent.delete(0, END)
                reg_ent.delete(0, END)
                pass_ent.delete(0, END)
            except ValueError as e:
                messagebox.showwarning("Validation", str(e))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        Button(
            self.content,
            text="Create Driver",
            bg="#0a84ff",
            fg="white",
            width=20,
            height=2,
            command=submit_driver
        ).pack(pady=12)

    # ---------------- Profile ----------------
    def show_profile(self):
        self.clear_content()

        Label(
            self.content,
            text="My Profile",
            font=("Arial", 18, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=20)

        if not self.admin_id:
            messagebox.showerror("Error", "Admin ID not available. Cannot load profile.")
            return

        try:
            row = self.service.get_profile()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch profile: {e}")
            return

        if not row:
            messagebox.showerror("Error", "Admin not found!")
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
                filename = f"admin_{self.admin_id}{ext}"
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
            ent.insert(0, values[i] if values[i] is not None else "")

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
                messagebox.showinfo("Success", "Profile updated successfully!")
            except ValueError as e:
                messagebox.showwarning("Warning", str(e))
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

    # ---------------- Logout & misc ----------------
    def logout(self):
        self._on_logout()

    def _on_logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            try:
                if self.logout_callback:
                    self.logout_callback()
                else:
                    self.root.destroy()
            except Exception:
                try:
                    self.root.destroy()
                except Exception:
                    pass

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

    # ---------------- Settings & Support ----------------
    def show_settings(self):
        self.clear_content()
        Label(
            self.content,
            text="Settings",
            font=("Arial", 18, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=20)

        frame = Frame(self.content, bg=self.color_content_bg)
        frame.pack(pady=10, padx=16, fill=X)

        Label(frame, text="Notification Preferences", bg=self.color_content_bg,
              font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=8, pady=6)

        self.email_notif_var = BooleanVar(value=True)
        self.sms_notif_var = BooleanVar(value=True)

        Checkbutton(frame, text="Email notifications", variable=self.email_notif_var,
                    bg=self.color_content_bg).grid(row=1, column=0, sticky="w", padx=20, pady=4)
        Checkbutton(frame, text="SMS notifications", variable=self.sms_notif_var,
                    bg=self.color_content_bg).grid(row=2, column=0, sticky="w", padx=20, pady=4)

        Label(
            frame,
            text="(Placeholder settings — wire to DB if needed.)",
            bg=self.color_content_bg,
            fg="#6b7280"
        ).grid(row=3, column=0, sticky="w", padx=8, pady=10)

    def show_support(self):
        self.clear_content()
        Label(
            self.content,
            text="Support",
            font=("Arial", 18, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=20)

        Label(
            self.content,
            text="If you face any issue with bookings, drivers, or users,\n"
                 "you can contact our support team.",
            font=("Arial", 12),
            bg=self.color_content_bg,
            justify="center"
        ).pack(pady=10)

        Button(
            self.content,
            text="Contact Support",
            bg=self.color_accent,
            fg="white",
            width=20,
            height=2,
            command=self._show_support_popup
        ).pack(pady=14)

    def _do_nothing(self):
        messagebox.showinfo("Coming Soon", "Feature not implemented yet ✨")

    def _show_support_popup(self):
        messagebox.showinfo(
            "Contact Support",
            "You can contact support at: support@example.com\n"
            "Or call: +977-9810000000"
        )

