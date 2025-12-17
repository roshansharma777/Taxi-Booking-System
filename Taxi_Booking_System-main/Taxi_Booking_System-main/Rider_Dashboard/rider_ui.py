from tkinter import *
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme_manager import get_theme_colors, save_theme_preference, get_theme_preference
from Rider_Dashboard.rider_service import RiderService


class RiderDashboard:
    def __init__(self, root, username, logout_callback=None):
        self.root = root
        self.username = username
        self.logout_callback = logout_callback

        # Initialize service layer
        try:
            self.service = RiderService(username)
            self.driver_id = self.service.driver_id
            self.driver_email = self.service.driver_email
            self.driver_name = self.service.driver_name
            # Load photo path from profile
            try:
                profile = self.service.get_profile()
                self.photo_path = profile[5] if profile and len(profile) > 5 else None
            except Exception:
                self.photo_path = None
        except Exception as e:
            messagebox.showerror("Driver Error", f"Failed to resolve driver: {e}")
            self.driver_id = None
            self.driver_email = None
            self.driver_name = None
            self.photo_path = None

        # Cache for image reference
        self.profile_img_tk = None

        # Initialize theme
        self.current_theme = get_theme_preference()
        self.colors = get_theme_colors(self.current_theme)
        self._update_color_vars()

        # window setup
        try:
            self.root.title(f"Driver Dashboard - {self.username}")
            self.root.geometry("1000x600")
        except Exception:
            pass
        self.root.configure(bg=self.color_content_bg)

        # Apply theme to treeview styles
        self._apply_treeview_theme()

        # Sidebar
        self.sidebar_frame = Frame(self.root, bg=self.color_sidebar_bg, width=220)
        self.sidebar_frame.pack(side=LEFT, fill=Y)
        self._create_sidebar()

        # Main content
        self.main_frame = Frame(self.root, bg=self.color_content_bg)
        self.main_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # Menu (File / Edit / View / Tools / Help)
        self.mainmenu = Menu(self.root)

        filemenu = Menu(self.mainmenu, tearoff=0)
        filemenu.add_command(label='New', command=self._do_nothing)
        filemenu.add_command(label='Open', command=self._do_nothing)
        filemenu.add_command(label='Save', command=self._do_nothing)
        filemenu.add_command(label='Save as...', command=self._do_nothing)
        filemenu.add_command(label='Close', command=self._do_nothing)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self._on_logout)
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
        viewmenu.add_command(label='Dashboard', command=self.show_dashboard)
        viewmenu.add_command(label='My Trips', command=self.show_trips)
        viewmenu.add_command(label='Profile', command=self.show_profile)
        viewmenu.add_command(label='Settings', command=self.show_settings)
        viewmenu.add_command(label='Support', command=self.show_support)
        viewmenu.add_command(label='Refresh', command=self.refresh_page)
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

        # Track current page for theme refresh
        self._current_page_method = self.show_trips
        
        # Start on trips
        self.show_trips()

    # ---------------- UI pieces ----------------
    def _create_sidebar(self):
        Label(
            self.sidebar_frame,
            text="Driver Menu",
            fg="white",
            bg=self.color_sidebar_bg,
            font=("Arial", 16, "bold"),
            pady=20
        ).pack()

        options = [
            ("Dashboard", self.show_dashboard),
            ("My Trips", self.show_trips),
            ("Profile", self.show_profile),
            ("Settings", self.show_settings),
            ("Support", self.show_support),
            ("Refresh", self.refresh_page),
        ]
        for text, command in options:
            btn = Button(
                self.sidebar_frame,
                text=text,
                fg="white",
                bg=self.color_sidebar_btn,
                activebackground=self.color_sidebar_btn_active,
                font=("Arial", 12),
                bd=0,
                relief="flat",
                command=command,
                cursor="hand2",
                width=20,
                height=2
            )
            btn.pack(pady=5, padx=10)

        # Theme toggle button
        self.theme_toggle_btn = Button(
            self.sidebar_frame,
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
            self.sidebar_frame,
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

    def _apply_treeview_theme(self):
        """Apply theme to treeview styles."""
        try:
            style = ttk.Style(self.root)
            style.configure(
                "Rider.Treeview",
                rowheight=22,
                padding=(2, 1),
                background=self.colors["treeview_bg"],
                foreground=self.colors["treeview_fg"],
                fieldbackground=self.colors["treeview_bg"]
            )
            style.configure(
                "Rider.Treeview.Heading",
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
        self.sidebar_frame.configure(bg=self.color_sidebar_bg)
        for widget in self.sidebar_frame.winfo_children():
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
        self.main_frame.configure(bg=self.color_content_bg)
        
        # Reapply treeview theme
        self._apply_treeview_theme()
        
        # Refresh current page
        if hasattr(self, '_current_page_method'):
            self._current_page_method()
        else:
            self.show_trips()

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # shared helper: sortable treeview
    def _make_treeview_sortable(self, tree, cols, numeric_cols=None):
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

    # ---------------- Dashboard ----------------
    def show_dashboard(self):
        self.clear_main()
        display = self.driver_name or self.driver_email or self.username

        # Hero
        Label(
            self.main_frame,
            text=f"Welcome, {display}",
            font=("Arial", 26, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=(20, 8))

        Label(
            self.main_frame,
            text="Snapshot of your driving activity",
            font=("Arial", 12),
            bg=self.color_content_bg,
            fg=self.color_text_secondary
        ).pack()

        # Stats cards
        cards = Frame(self.main_frame, bg=self.color_content_bg)
        cards.pack(pady=20, padx=20, fill=X)

        try:
            stats = self.service.get_stats()
            total_assigned = stats.get("assigned", 0)
            total_active = stats.get("active", 0)
            total_completed = stats.get("completed", 0)
        except Exception:
            total_assigned = total_active = total_completed = 0

        def card(parent, emoji, value, label, color):
            outer = Frame(parent, bg=self.color_card_bg, relief="flat", bd=1)
            outer.pack(side=LEFT, padx=10, fill=BOTH, expand=True)
            inner = Frame(outer, bg=self.color_card_bg)
            inner.pack(padx=20, pady=20, fill=BOTH)
            Label(inner, text=emoji, font=("Arial", 30), bg=self.color_card_bg).pack()
            Label(inner, text=str(value), font=("Arial", 28, "bold"), bg=self.color_card_bg, fg=color).pack()
            Label(inner, text=label, font=("Arial", 12), bg=self.color_card_bg, fg=self.color_card_text_secondary).pack()

        card(cards, "🗂️", total_assigned, "Assigned", "#2563eb")
        card(cards, "🚗", total_active, "Active / Accepted", "#f59e0b")
        card(cards, "✅", total_completed, "Completed", "#16a34a")

        # Hint
        Label(
            self.main_frame,
            text="Use the menu to view trips or manage your profile.",
            font=("Arial", 12),
            bg=self.color_content_bg,
            fg="#4b5563"
        ).pack(pady=(10, 0))

    # ---------------- Trips view ----------------
    def show_trips(self):
        self._current_page_method = self.show_trips
        self.clear_main()
        Label(
            self.main_frame,
            text="My Assigned Trips",
            font=("Arial", 20, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=10)

        # Search / filter bar
        search_frame = Frame(self.main_frame, bg=self.color_content_bg)
        search_frame.pack(fill=X, padx=12, pady=(0, 5))
        Label(search_frame, text="Search:", bg=self.color_content_bg, font=("Arial", 11)).pack(side=LEFT, padx=(0, 4))
        self.trips_search_var = StringVar()
        search_entry = Entry(search_frame, textvariable=self.trips_search_var, width=22)
        search_entry.pack(side=LEFT, padx=(0, 10))

        Label(search_frame, text="Status:", bg=self.color_content_bg, font=("Arial", 11)).pack(side=LEFT, padx=(0, 4))
        self.trips_status_var = StringVar(value="All")
        status_cb = ttk.Combobox(
            search_frame,
            textvariable=self.trips_status_var,
            values=["All", "Pending", "Accepted", "Completed", "Cancelled"],
            width=12,
            state="readonly",
        )
        status_cb.pack(side=LEFT, padx=(0, 10))

        Label(search_frame, text="Customer:", bg=self.color_content_bg, font=("Arial", 11)).pack(side=LEFT, padx=(0, 4))
        self.trips_customer_var = StringVar()
        customer_entry = Entry(search_frame, textvariable=self.trips_customer_var, width=18)
        customer_entry.pack(side=LEFT, padx=(0, 10))

        Label(search_frame, text="From (YYYY-MM-DD):", bg=self.color_content_bg, font=("Arial", 10)).pack(side=LEFT, padx=(0, 4))
        self.trips_from_var = StringVar()
        from_entry = Entry(search_frame, textvariable=self.trips_from_var, width=12)
        from_entry.pack(side=LEFT, padx=(0, 4))

        Label(search_frame, text="To:", bg=self.color_content_bg, font=("Arial", 10)).pack(side=LEFT, padx=(0, 4))
        self.trips_to_var = StringVar()
        to_entry = Entry(search_frame, textvariable=self.trips_to_var, width=12)
        to_entry.pack(side=LEFT, padx=(0, 4))

        table_frame = Frame(self.main_frame, bg=self.color_content_bg)
        table_frame.pack(fill=BOTH, expand=True, padx=12, pady=8)

        columns = (
            "Booking ID", "Customer Email", "Pickup", "Dropoff",
            "Date", "Time", "Assigned Driver", "Status", "Ride Start", "Ride Completion"
        )
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15, style="Rider.Treeview")

        # striped rows
        self.tree.tag_configure("evenrow", background=self.colors["treeview_even"])
        self.tree.tag_configure("oddrow", background=self.colors["treeview_odd"])

        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Booking ID":
                self.tree.column(col, width=70, anchor=CENTER, stretch=False)
            elif col in ("Date", "Time"):
                self.tree.column(col, width=90, anchor=CENTER, stretch=False)
            elif col == "Status":
                self.tree.column(col, width=95, anchor=CENTER, stretch=False)
            elif col in ("Ride Start", "Ride Completion"):
                self.tree.column(col, width=140, anchor=CENTER, stretch=False)
            elif col == "Customer Email":
                self.tree.column(col, width=150, stretch=True)
            elif col == "Assigned Driver":
                self.tree.column(col, width=120, stretch=True)
            else:  # Pickup / Dropoff
                self.tree.column(col, width=120, stretch=True)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar_y = Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        scrollbar_y.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        # sortable columns
        self._make_treeview_sortable(self.tree, columns, numeric_cols={"Booking ID"})

        btn_frame = Frame(self.main_frame, bg=self.color_content_bg)
        btn_frame.pack(pady=8)
        Button(
            btn_frame, text="Accept Ride", bg="#0a84ff", fg="white",
            width=14, command=self.accept_ride
        ).pack(side=LEFT, padx=6)
        Button(
            btn_frame, text="Complete Ride", bg="#16a34a", fg="white",
            width=14, command=self.complete_ride
        ).pack(side=LEFT, padx=6)
        Button(
            btn_frame, text="Refresh", bg="#6b7280", fg="white",
            width=10, command=self.refresh_page
        ).pack(side=LEFT, padx=6)

        # cache + initial load
        try:
            self._trips_cache = self.service.get_trips()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load trips: {e}")
            self._trips_cache = []

        def _refresh_tree(filtered=None):
            for row in self.tree.get_children():
                self.tree.delete(row)
            data = filtered if filtered is not None else getattr(self, "_trips_cache", [])
            for idx, trip in enumerate(data):
                driver_disp = self.driver_name or self.driver_email or ""
                # Format timestamps for display
                ride_start = trip.get("ride_start_timestamp")
                if ride_start:
                    if isinstance(ride_start, str):
                        ride_start_display = ride_start
                    else:
                        ride_start_display = ride_start.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    ride_start_display = "N/A"
                
                ride_completion = trip.get("ride_completion_timestamp")
                if ride_completion:
                    if isinstance(ride_completion, str):
                        ride_completion_display = ride_completion
                    else:
                        ride_completion_display = ride_completion.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    ride_completion_display = "N/A"
                
                vals = [
                    trip["id"],
                    trip["customer_email"],
                    trip["pickup"],
                    trip["dropoff"],
                    trip["date"],
                    trip["time"],
                    driver_disp,
                    trip["status"],
                    ride_start_display,
                    ride_completion_display
                ]
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.tree.insert("", END, values=vals, tags=(tag,))

        def _apply_filters(*_):
            text = (self.trips_search_var.get() or "").strip().lower()
            status_filter = (self.trips_status_var.get() or "All").strip().lower()
            cust_filter = (self.trips_customer_var.get() or "").strip().lower()
            from_date = (self.trips_from_var.get() or "").strip()
            to_date = (self.trips_to_var.get() or "").strip()

            filtered = []
            for trip in getattr(self, "_trips_cache", []):
                status_val = str(trip.get("status", ""))
                customer_val = str(trip.get("customer_email", ""))
                date_str = str(trip.get("date", ""))

                if text:
                    combined = " ".join(
                        str(trip.get(k, ""))
                        for k in ("id", "customer_email", "pickup", "dropoff", "date", "time", "status")
                    ).lower()
                    if text not in combined:
                        continue

                if status_filter and status_filter != "all":
                    if status_val.lower() != status_filter:
                        continue

                if cust_filter and cust_filter not in customer_val.lower():
                    continue

                if from_date and date_str and date_str < from_date:
                    continue
                if to_date and date_str and date_str > to_date:
                    continue

                filtered.append(trip)

            _refresh_tree(filtered)

        search_entry.bind("<KeyRelease>", _apply_filters)
        status_cb.bind("<<ComboboxSelected>>", _apply_filters)
        customer_entry.bind("<KeyRelease>", _apply_filters)
        from_entry.bind("<KeyRelease>", _apply_filters)
        to_entry.bind("<KeyRelease>", _apply_filters)
        _refresh_tree()

    def load_trips(self):
        if not self.driver_id:
            return

        try:
            self._trips_cache = self.service.get_trips()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load trips: {e}")
            self._trips_cache = []

        # reapply current search / status / customer / date filters, if any
        try:
            text = (self.trips_search_var.get() or "").strip().lower()
        except Exception:
            text = ""
        try:
            status_filter = (self.trips_status_var.get() or "All").strip().lower()
        except Exception:
            status_filter = "all"
        try:
            cust_filter = (self.trips_customer_var.get() or "").strip().lower()
        except Exception:
            cust_filter = ""
        try:
            from_date = (self.trips_from_var.get() or "").strip()
        except Exception:
            from_date = ""
        try:
            to_date = (self.trips_to_var.get() or "").strip()
        except Exception:
            to_date = ""

        if text or status_filter != "all" or cust_filter or from_date or to_date:
            filtered = []
            for trip in getattr(self, "_trips_cache", []):
                combined = " ".join(
                    str(trip.get(k, "")) for k in ("id", "customer_email", "pickup", "dropoff", "date", "time", "status")
                ).lower()
                status_val = str(trip.get("status", ""))
                customer_val = str(trip.get("customer_email", ""))
                date_str = str(trip.get("date", ""))

                if text and text not in combined:
                    continue
                if status_filter and status_filter != "all" and status_val.lower() != status_filter:
                    continue
                if cust_filter and cust_filter not in customer_val.lower():
                    continue
                if from_date and date_str and date_str < from_date:
                    continue
                if to_date and date_str and date_str > to_date:
                    continue

                filtered.append(trip)
            # reuse local-like refresh
            for row in self.tree.get_children():
                self.tree.delete(row)
            for idx, trip in enumerate(filtered):
                driver_disp = self.driver_name or self.driver_email or ""
                # Format timestamps for display
                ride_start = trip.get("ride_start_timestamp")
                if ride_start:
                    if isinstance(ride_start, str):
                        ride_start_display = ride_start
                    else:
                        ride_start_display = ride_start.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    ride_start_display = "N/A"
                
                ride_completion = trip.get("ride_completion_timestamp")
                if ride_completion:
                    if isinstance(ride_completion, str):
                        ride_completion_display = ride_completion
                    else:
                        ride_completion_display = ride_completion.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    ride_completion_display = "N/A"
                
                vals = [
                    trip["id"],
                    trip["customer_email"],
                    trip["pickup"],
                    trip["dropoff"],
                    trip["date"],
                    trip["time"],
                    driver_disp,
                    trip["status"],
                    ride_start_display,
                    ride_completion_display
                ]
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.tree.insert("", END, values=vals, tags=(tag,))
        else:
            for row in self.tree.get_children():
                self.tree.delete(row)
            data = getattr(self, "_trips_cache", [])
            # if only status filter is active
            if status_filter and status_filter != "all":
                data = [
                    trip for trip in data if str(trip.get("status", "")).lower() == status_filter
                ]

            for idx, trip in enumerate(data):
                driver_disp = self.driver_name or self.driver_email or ""
                # Format timestamps for display
                ride_start = trip.get("ride_start_timestamp")
                if ride_start:
                    if isinstance(ride_start, str):
                        ride_start_display = ride_start
                    else:
                        ride_start_display = ride_start.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    ride_start_display = "N/A"
                
                ride_completion = trip.get("ride_completion_timestamp")
                if ride_completion:
                    if isinstance(ride_completion, str):
                        ride_completion_display = ride_completion
                    else:
                        ride_completion_display = ride_completion.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    ride_completion_display = "N/A"
                
                vals = [
                    trip["id"],
                    trip["customer_email"],
                    trip["pickup"],
                    trip["dropoff"],
                    trip["date"],
                    trip["time"],
                    driver_disp,
                    trip["status"],
                    ride_start_display,
                    ride_completion_display
                ]
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.tree.insert("", END, values=vals, tags=(tag,))

    # ---------------- Actions ----------------
    def get_selected_booking(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a booking first.")
            return None
        vals = self.tree.item(sel[0])["values"]
        if not vals:
            return None
        return vals[0]

    def accept_ride(self):
        booking_id = self.get_selected_booking()
        if not booking_id:
            return
        try:
            self.service.accept_ride(booking_id)
            messagebox.showinfo("Success", "Ride accepted.")
            self.load_trips()
        except ValueError as e:
            messagebox.showinfo("Info", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to accept ride: {e}")

    def complete_ride(self):
        booking_id = self.get_selected_booking()
        if not booking_id:
            return
        try:
            self.service.complete_ride(booking_id)
            messagebox.showinfo("Success", "Ride completed.")
            self.load_trips()
        except ValueError as e:
            messagebox.showinfo("Info", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete ride: {e}")

    # ---------------- Profile ----------------
    def show_profile(self):
        self.clear_main()

        Label(
            self.main_frame,
            text="My Profile",
            font=("Arial", 18, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=20)

        if not self.driver_id:
            messagebox.showerror("Error", "Driver ID not resolved. Cannot load profile.")
            return

        try:
            row = self.service.get_profile()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load driver profile: {e}")
            return

        if not row:
            messagebox.showerror("Error", "Driver not found!")
            return

        if len(row) == 6:
            name, email, phone, address, status, db_photo_path = row
            self.photo_path = db_photo_path
        else:
            name, email, phone, address, status = row

        # ---------- Photo + Upload ----------
        photo_frame = Frame(self.main_frame, bg=self.color_content_bg)
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
                text=(name[:1].upper() if name else "?"),
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
                filename = f"driver_{self.driver_id}{ext}"
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
        frame = Frame(self.main_frame, bg=self.color_content_bg)
        frame.pack(pady=10)

        labels = ["Name", "Email", "Phone", "Address", "Status"]
        values = [name, email, phone, address, status]
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
            if lab in ["Email", "Status"]:
                ent.config(state="disabled")
            ent.grid(row=i, column=1, padx=10, pady=7)
            entries[lab] = ent

        def update():
            new_name = entries["Name"].get()
            new_phone = entries["Phone"].get()
            new_address = entries["Address"].get()

            try:
                self.service.update_profile(new_name, new_phone, new_address)
                self.driver_name = new_name
                messagebox.showinfo("Success", "Profile updated successfully!")
            except ValueError as e:
                messagebox.showwarning("Warning", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update profile: {e}")

        Button(
            self.main_frame,
            text="Save Changes",
            bg=self.color_accent,
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            command=update
        ).pack(pady=20)

    # ---------------- Utilities ----------------
    def refresh_page(self):
        try:
            self.show_dashboard()
        except Exception:
            pass
        try:
            self.load_trips()
        except Exception:
            pass

    # ---------------- Misc helpers ----------------
    def _do_nothing(self):
        messagebox.showinfo("Coming Soon", "Feature not implemented yet ✨")

    def _show_support_popup(self):
        messagebox.showinfo(
            "Contact Support",
            "You can contact support at: support@example.com\n"
            "Or call: +977-9810000000"
        )

    # ---------------- Settings & Support ----------------
    def show_settings(self):
        self.clear_main()
        Label(
            self.main_frame,
            text="Settings",
            font=("Arial", 18, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=20)

        frame = Frame(self.main_frame, bg=self.color_content_bg)
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
        self.clear_main()
        Label(
            self.main_frame,
            text="Support",
            font=("Arial", 18, "bold"),
            bg=self.color_content_bg,
            fg=self.color_accent
        ).pack(pady=20)

        Label(
            self.main_frame,
            text="If you face any issue with your trips or profile,\n"
                 "you can contact our support team.",
            font=("Arial", 12),
            bg=self.color_content_bg,
            justify="center"
        ).pack(pady=10)

        Button(
            self.main_frame,
            text="Contact Support",
            bg=self.color_accent,
            fg="white",
            width=20,
            height=2,
            command=lambda: messagebox.showinfo(
                "Contact Support",
                "You can contact support at: support@example.com\n"
                "Or call: +977-9810000000"
            )
        ).pack(pady=14)

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
            self.sidebar_frame.destroy()
        except Exception:
            pass
        try:
            self.main_frame.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    root = Tk()
    RiderDashboard(root, username="rupak@gmail.com")
    root.mainloop()

