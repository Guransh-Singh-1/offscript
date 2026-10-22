import json
import os
import re
import datetime
import calendar
import tkinter as tk
from tkinter import messagebox, ttk

class CalendarDialog(tk.Toplevel):
    def __init__(self, parent, initial_date=None, colors=None):
        super().__init__(parent)
        self.title("Select Date")
        self.geometry("320x360")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.colors = colors or {
            "bg": "#0F172A",
            "card_bg": "#1E293B",
            "card_border": "#334155",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "accent_blue": "#38BDF8"
        }
        self.configure(bg=self.colors["bg"])
        
        self.update_idletasks()
        w = 320
        h = 360
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        if initial_date:
            try:
                dt = datetime.datetime.strptime(initial_date, "%Y-%m-%d")
                self.selected_year = dt.year
                self.selected_month = dt.month
                self.selected_day = dt.day
            except ValueError:
                dt = datetime.date.today()
                self.selected_year, self.selected_month, self.selected_day = dt.year, dt.month, dt.day
        else:
            dt = datetime.date.today()
            self.selected_year, self.selected_month, self.selected_day = dt.year, dt.month, dt.day
        self.curr_year = self.selected_year
        self.curr_month = self.selected_month
        self.result_date = None
        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self, bg=self.colors["card_bg"], pady=10)
        header.pack(fill="x")
        prev_btn = tk.Button(header, text="◄", font=("Segoe UI", 10, "bold"),
                             fg=self.colors["accent_blue"], bg=self.colors["card_bg"],
                             bd=0, activebackground=self.colors["card_bg"],
                             activeforeground="#0284C7", cursor="hand2", command=self.prev_month)
        prev_btn.pack(side="left", padx=15)
        self.month_lbl = tk.Label(header, font=("Segoe UI", 11, "bold"),
                                  fg=self.colors["text_primary"], bg=self.colors["card_bg"])
        self.month_lbl.pack(side="left", expand=True)
        next_btn = tk.Button(header, text="►", font=("Segoe UI", 10, "bold"),
                             fg=self.colors["accent_blue"], bg=self.colors["card_bg"],
                             bd=0, activebackground=self.colors["card_bg"],
                             activeforeground="#0284C7", cursor="hand2", command=self.next_month)
        next_btn.pack(side="right", padx=15)
        days_frame = tk.Frame(self, bg=self.colors["bg"], pady=5)
        days_frame.pack(fill="x", padx=10)
        for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            lbl = tk.Label(days_frame, text=day, width=4, font=("Segoe UI", 9, "bold"),
                           fg=self.colors["text_secondary"], bg=self.colors["bg"])
            lbl.pack(side="left", expand=True)
        self.grid_frame = tk.Frame(self, bg=self.colors["bg"])
        self.grid_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.render_calendar()

    def render_calendar(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.month_lbl.config(text=f"{calendar.month_name[self.curr_month]} {self.curr_year}")
        cal = calendar.monthcalendar(self.curr_year, self.curr_month)
        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    lbl = tk.Label(self.grid_frame, text="", width=4, bg=self.colors["bg"])
                    lbl.grid(row=row_idx, column=col_idx, padx=2, pady=2)
                else:
                    is_selected = (day == self.selected_day and 
                                   self.curr_month == self.selected_month and 
                                   self.curr_year == self.selected_year)
                    bg_color = self.colors["accent_blue"] if is_selected else self.colors["card_bg"]
                    fg_color = "#0F172A" if is_selected else self.colors["text_primary"]
                    btn = tk.Button(self.grid_frame, text=str(day), width=4, font=("Segoe UI", 9, "bold" if is_selected else "normal"),
                                    bg=bg_color, fg=fg_color, bd=0, cursor="hand2",
                                    activebackground=self.colors["accent_blue"],
                                    command=lambda d=day: self.select_day(d))
                    btn.grid(row=row_idx, column=col_idx, padx=2, pady=2)

    def prev_month(self):
        if self.curr_month == 1:
            self.curr_month = 12
            self.curr_year -= 1
        else:
            self.curr_month -= 1
        self.render_calendar()

    def next_month(self):
        if self.curr_month == 12:
            self.curr_month = 1
            self.curr_year += 1
        else:
            self.curr_month += 1
        self.render_calendar()

    def select_day(self, day):
        self.result_date = f"{self.curr_year:04d}-{self.curr_month:02d}-{day:02d}"
        self.destroy()

class EditTransactionDialog(tk.Toplevel):
    def __init__(self, parent, transaction, colors=None):
        super().__init__(parent)
        self.title("Edit Payment Entry")
        self.geometry("420x460")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.colors = colors or {
            "bg": "#0F172A",
            "card_bg": "#1E293B",
            "card_border": "#334155",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "accent_blue": "#38BDF8",
            "accent_yellow": "#EAB308",
            "input_bg": "#0F172A"
        }
        self.configure(bg=self.colors["bg"])
        
        self.update_idletasks()
        w = 420
        h = 460
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.transaction = transaction
        self.updated_data = None
        self.build_ui()

    def build_ui(self):
        container = tk.Frame(self, bg=self.colors["card_bg"], bd=1, relief="solid", highlightbackground=self.colors["accent_yellow"])
        container.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(container, text="✏️ Edit Scheduled Payment", font=("Segoe UI", 11, "bold"), fg=self.colors["accent_yellow"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(15, 10))

        tk.Label(container, text="Payee Name:", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(2, 0))
        self.title_entry = tk.Entry(container, font=("Segoe UI", 9), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.title_entry.pack(fill="x", padx=15, pady=3, ipady=4)
        self.title_entry.insert(0, self.transaction.get("title", ""))

        tk.Label(container, text="Amount in ₹:", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(5, 0))
        self.amount_entry = tk.Entry(container, font=("Segoe UI", 9), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.amount_entry.pack(fill="x", padx=15, pady=3, ipady=4)
        self.amount_entry.insert(0, str(self.transaction.get("amount", "")))

        tk.Label(container, text="Date (yyyy-mm-dd):", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(5, 0))
        date_frame = tk.Frame(container, bg=self.colors["card_bg"])
        date_frame.pack(fill="x", padx=15, pady=3)
        self.date_entry = tk.Entry(date_frame, font=("Segoe UI", 9), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.date_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.date_entry.insert(0, self.transaction.get("date", datetime.date.today().strftime("%Y-%m-%d")))
        cal_btn = tk.Button(date_frame, text="📅", font=("Segoe UI", 8), bg=self.colors["accent_blue"], fg="#0F172A", bd=0, cursor="hand2", command=self.open_calendar)
        cal_btn.pack(side="right", padx=(5, 0), ipady=3, ipadx=5)

        tk.Label(container, text="Category:", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(5, 0))
        self.category_combobox = ttk.Combobox(container, values=["Subscription", "EMI", "Utility", "Food & Dining", "Groceries", "Transport", "Other"], font=("Segoe UI", 9), state="readonly")
        self.category_combobox.pack(fill="x", padx=15, pady=3, ipady=3)
        self.category_combobox.set(self.transaction.get("category", "Subscription"))

        tk.Label(container, text="Payment Method & Billing Frequency:", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(5, 0))
        row_freq = tk.Frame(container, bg=self.colors["card_bg"])
        row_freq.pack(fill="x", padx=15, pady=3)
        self.type_combobox = ttk.Combobox(row_freq, values=["UPI Autopay", "Card Autopay", "Bank Standing Instruction"], font=("Segoe UI", 9), state="readonly")
        self.type_combobox.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=3)
        self.type_combobox.set(self.transaction.get("source", "UPI Autopay"))

        self.frequency_combobox = ttk.Combobox(row_freq, values=["Monthly", "Annually", "One-Time"], font=("Segoe UI", 9), state="readonly")
        self.frequency_combobox.pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=3)
        self.frequency_combobox.set(self.transaction.get("frequency", "Monthly"))

        btn_frame = tk.Frame(container, bg=self.colors["card_bg"])
        btn_frame.pack(fill="x", padx=15, pady=(15, 10))

        save_btn = tk.Button(btn_frame, text="💾 Save Changes", font=("Segoe UI", 10, "bold"), bg=self.colors["accent_yellow"], fg="#0F172A", bd=0, cursor="hand2", command=self.save)
        save_btn.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=6)

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 10), bg=self.colors["card_border"], fg="white", bd=0, cursor="hand2", command=self.destroy)
        cancel_btn.pack(side="right", fill="x", expand=True, padx=(5, 0), ipady=6)

    def open_calendar(self):
        dialog = CalendarDialog(self, initial_date=self.date_entry.get().strip(), colors=self.colors)
        self.wait_window(dialog)
        if dialog.result_date:
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, dialog.result_date)

    def save(self):
        title = self.title_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        date_str = self.date_entry.get().strip()
        category = self.category_combobox.get()
        payment_type = self.type_combobox.get()
        frequency = self.frequency_combobox.get()

        if not title:
            messagebox.showerror("Error", "Please enter a payee title.")
            return
        try:
            amount = float(amount_str)
            if amount <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount.")
            return

        status = "Pending" if category in ["Utility", "Bills & Utilities"] else self.transaction.get("status", "Paid")
        is_recurring = frequency != "One-Time"

        self.updated_data = {
            "date": date_str,
            "title": title,
            "category": category,
            "amount": amount,
            "frequency": frequency,
            "source": payment_type,
            "status": status,
            "recurring": is_recurring,
            "selected": self.transaction.get("selected", False)
        }
        self.destroy()

class ModernFinPulseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FinPulse — Unified Recurring Spend Tracker & Subscription Killer")
        self.root.geometry("1280x850")
        self.root.minsize(1100, 750)
        self.root.configure(bg="#0F172A")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(script_dir, "finpulse_data.json")
        self.transactions = self.load_data()
        self.active_filter = "All"
        
        self.banner_timer_id = None
        self.active_alerts_list = []
        self.current_alert_index = 0

        self.colors = {
            "bg": "#0F172A",
            "sidebar_bg": "#1E293B",
            "card_bg": "#1E293B",
            "card_border": "#334155",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "accent_blue": "#38BDF8",
            "accent_green": "#22C55E",
            "accent_purple": "#A855F7",
            "accent_red": "#EF4444",
            "accent_yellow": "#EAB308",
            "input_bg": "#0F172A",
            "button_green": "#16A34A",
            "button_green_hover": "#15803D"
        }
        self.apply_ttk_styles()
        self.build_layout()
        self.refresh_ui()

    def apply_ttk_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#1E293B",
                        foreground="#F8FAFC",
                        fieldbackground="#1E293B",
                        rowheight=34,
                        font=("Segoe UI", 10),
                        borderwidth=0)
        style.map("Treeview", background=[("selected", "#38BDF8")], foreground=[("selected", "#0F172A")])
        style.configure("Treeview.Heading",
                        background="#334155",
                        foreground="#F8FAFC",
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0)
        style.configure("Dark.TCheckbutton",
                        background=self.colors["card_bg"],
                        foreground=self.colors["text_primary"],
                        font=("Segoe UI", 9))
        style.map("Dark.TCheckbutton",
                  background=[("active", self.colors["card_bg"])],
                  foreground=[("active", self.colors["text_primary"])])

    def build_layout(self):
        top_bar = tk.Frame(self.root, bg=self.colors["bg"])
        top_bar.pack(fill="x", padx=25, pady=(15, 10))

        title_frame = tk.Frame(top_bar, bg=self.colors["bg"])
        title_frame.pack(side="left")
        tk.Label(title_frame, text="FinPulse", font=("Segoe UI", 20, "bold"), fg=self.colors["text_primary"], bg=self.colors["bg"]).pack(anchor="w")
        tk.Label(title_frame, text="Unified recurring spend tracker & automated subscription manager", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["bg"]).pack(anchor="w")

        live_badge = tk.Label(top_bar, text="● Live Transaction Engine", font=("Segoe UI", 9, "bold"), fg=self.colors["accent_green"], bg="#064E3B", padx=12, pady=6)
        live_badge.pack(side="right")

        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        stats_frame = tk.Frame(main_container, bg=self.colors["bg"])
        stats_frame.pack(fill="x", pady=(0, 15))

        self.card_committed = self.create_stat_card(stats_frame, "COMMITTED MONTHLY", "₹0.00", "Pre-allocated before discretionary spend")
        self.card_committed.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.card_emis = self.create_stat_card(stats_frame, "MONTHLY EMIs", "₹0.00", "Total monthly debt obligations")
        self.card_emis.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.card_due = self.create_stat_card(stats_frame, "DUE IN 7 DAYS", "0 Bills", "Action required soon")
        self.card_due.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.card_mandates = self.create_stat_card(stats_frame, "ACTIVE PAYMENTS", "0 Total", "UPI Autopay & Card Standing Instructions")
        self.card_mandates.pack(side="left", fill="x", expand=True)

        self.banner_card = tk.Frame(main_container, bg="#064E3B", highlightbackground="#059669", highlightthickness=1)
        self.banner_card.pack(fill="x", pady=(0, 15), ipady=8, ipadx=12)
        
        banner_top = tk.Frame(self.banner_card, bg="#064E3B")
        banner_top.pack(fill="x", padx=10, pady=(2, 0))

        self.banner_title = tk.Label(banner_top, text="✅ Financial Health: Looking Great!", font=("Segoe UI", 10, "bold"), fg="#34D399", bg="#064E3B")
        self.banner_title.pack(side="left", anchor="w")

        self.banner_action_btn = tk.Button(banner_top, text="", font=("Segoe UI", 8, "bold"), bd=0, cursor="hand2", padx=8, pady=2)
        self.banner_action_btn.pack(side="right")
        self.banner_action_btn.pack_forget()

        self.banner_desc = tk.Label(self.banner_card, text="Analyzing your active recurring transactions and financial health...", font=("Segoe UI", 9), fg="#A7F3D0", bg="#064E3B")
        self.banner_desc.pack(anchor="w", padx=10, pady=(0, 2))

        inputs_frame = tk.Frame(main_container, bg=self.colors["bg"])
        inputs_frame.pack(fill="x", pady=(0, 15))

        upi_card = tk.LabelFrame(inputs_frame, text=" Smart Bank / UPI SMS Ingestion ", font=("Segoe UI", 10, "bold"),
                                 bg=self.colors["card_bg"], fg=self.colors["accent_blue"],
                                 bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        upi_card.pack(side="left", fill="both", expand=True, padx=(0, 10), ipadx=10, ipady=10)

        tk.Label(upi_card, text="Select sample notification or type custom message below:", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=10, pady=(2, 2))
        
        self.sample_combobox = ttk.Combobox(upi_card, values=[
            "Select sample notification...",
            "A/c XX1234 debited by INR 649.00 on 2026-10-22 to NETFLIX via UPI Ref 928301",
            "A/c XX1234 bill generated for INR 1,450.00 on 2026-10-22 from BESCOM Utility due soon",
            "A/c XX1234 debited by INR 12,500.00 on 2026-10-22 to HDFC LOAN EMI via UPI Ref 928303",
            "A/c XX1234 debited by INR 450.00 on 2026-10-22 to SWIGGY via UPI Ref 928304"
        ], font=("Segoe UI", 9), state="readonly")
        self.sample_combobox.pack(fill="x", padx=10, pady=(0, 4), ipady=3)
        self.sample_combobox.set("Select sample notification...")
        self.sample_combobox.bind("<<ComboboxSelected>>", self.load_sample_sms)

        self.upi_sms_entry = tk.Entry(upi_card, font=("Segoe UI", 9), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white", bd=1, relief="solid")
        self.upi_sms_entry.pack(fill="x", padx=10, pady=2, ipady=6)
        self.upi_sms_entry.insert(0, "A/c XX1234 bill generated for INR 1,450.00 on 2026-10-22 from BESCOM Utility due soon")

        parse_btn = tk.Button(upi_card, text="Scan & Add Transaction", font=("Segoe UI", 10, "bold"),
                              bg=self.colors["accent_blue"], fg="#0F172A", activebackground="#0284C7",
                              bd=0, cursor="hand2", command=self.parse_upi_sms)
        parse_btn.pack(fill="x", padx=10, pady=(8, 5), ipady=6)

        self.manual_card = tk.LabelFrame(inputs_frame, text=" Add Payment Manually ", font=("Segoe UI", 10, "bold"),
                                         bg=self.colors["card_bg"], fg=self.colors["text_primary"],
                                         bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        self.manual_card.pack(side="right", fill="both", expand=True, ipadx=10, ipady=10)

        form_grid = tk.Frame(self.manual_card, bg=self.colors["card_bg"])
        form_grid.pack(fill="x", padx=10, pady=5)

        r0_c0 = tk.Frame(form_grid, bg=self.colors["card_bg"])
        r0_c0.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(r0_c0, text="Payee Name (e.g. Gym, Rent)", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 0))
        self.title_entry = tk.Entry(r0_c0, font=("Segoe UI", 9), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.title_entry.pack(fill="x", pady=2, ipady=4)

        r0_c1 = tk.Frame(form_grid, bg=self.colors["card_bg"])
        r0_c1.pack(side="left", fill="x", expand=True, padx=5)
        tk.Label(r0_c1, text="Amount in ₹", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 0))
        self.amount_entry = tk.Entry(r0_c1, font=("Segoe UI", 9), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.amount_entry.pack(fill="x", pady=2, ipady=4)

        r0_c2 = tk.Frame(form_grid, bg=self.colors["card_bg"])
        r0_c2.pack(side="left", fill="x", expand=True, padx=(5, 0))
        tk.Label(r0_c2, text="Date (yyyy-mm-dd)", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 0))
        date_box_frame = tk.Frame(r0_c2, bg=self.colors["card_bg"])
        date_box_frame.pack(fill="x", pady=2)
        self.date_entry = tk.Entry(date_box_frame, font=("Segoe UI", 9), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.date_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        cal_btn = tk.Button(date_box_frame, text="📅", font=("Segoe UI", 8), bg=self.colors["accent_blue"], fg="#0F172A", bd=0, cursor="hand2", command=self.open_calendar_picker)
        cal_btn.pack(side="right", padx=(3, 0), ipady=3, ipadx=5)

        form_grid2 = tk.Frame(self.manual_card, bg=self.colors["card_bg"])
        form_grid2.pack(fill="x", padx=10, pady=(0, 5))

        r1_c0 = tk.Frame(form_grid2, bg=self.colors["card_bg"])
        r1_c0.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(r1_c0, text="Category", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 0))
        self.category_combobox = ttk.Combobox(r1_c0, values=["Subscription", "EMI", "Utility", "Food & Dining", "Groceries", "Transport", "Other"], font=("Segoe UI", 9), state="readonly")
        self.category_combobox.pack(fill="x", pady=2, ipady=3)
        self.category_combobox.set("Utility")

        r1_c1 = tk.Frame(form_grid2, bg=self.colors["card_bg"])
        r1_c1.pack(side="left", fill="x", expand=True, padx=5)
        tk.Label(r1_c1, text="Payment Method", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 0))
        self.type_combobox = ttk.Combobox(r1_c1, values=["UPI Autopay", "Card Autopay", "Bank Standing Instruction"], font=("Segoe UI", 9), state="readonly")
        self.type_combobox.pack(fill="x", pady=2, ipady=3)
        self.type_combobox.set("UPI Autopay")

        r1_c2 = tk.Frame(form_grid2, bg=self.colors["card_bg"])
        r1_c2.pack(side="left", fill="x", expand=True, padx=(5, 0))
        tk.Label(r1_c2, text="Billing Frequency", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 0))
        self.frequency_combobox = ttk.Combobox(r1_c2, values=["Monthly", "Annually", "One-Time"], font=("Segoe UI", 9), state="readonly")
        self.frequency_combobox.pack(fill="x", pady=2, ipady=3)
        self.frequency_combobox.set("Monthly")

        form_grid3 = tk.Frame(self.manual_card, bg=self.colors["card_bg"])
        form_grid3.pack(fill="x", padx=10, pady=(5, 5))

        self.save_btn = tk.Button(form_grid3, text="+ Add Payment Entry", font=("Segoe UI", 10, "bold"),
                                  bg="#6366F1", fg="white", activebackground="#4F46E5",
                                  bd=0, cursor="hand2", command=self.add_transaction)
        self.save_btn.pack(side="left", fill="x", expand=True, ipady=6)

        table_card = tk.LabelFrame(main_container, text=" Active Scheduled Payments ", font=("Segoe UI", 11, "bold"),
                                    bg=self.colors["card_bg"], fg=self.colors["text_primary"],
                                    bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        table_card.pack(fill="both", expand=True)

        table_header_frame = tk.Frame(table_card, bg=self.colors["card_bg"])
        table_header_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(table_header_frame, text="All recurring transactions and active standing instructions", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(side="left")

        filter_frame = tk.Frame(table_header_frame, bg=self.colors["card_bg"])
        filter_frame.pack(side="right")
        for f_name in ["All", "Subscription", "EMI", "Utility"]:
            btn = tk.Button(filter_frame, text=f_name, font=("Segoe UI", 9, "bold"),
                            bg=self.colors["accent_blue"] if f_name=="All" else self.colors["card_border"],
                            fg="#0F172A" if f_name=="All" else "white", bd=0, padx=10, pady=3, cursor="hand2",
                            command=lambda fn=f_name: self.set_filter(fn))
            btn.pack(side="left", padx=2)
            setattr(self, f"filter_btn_{f_name.lower()}", btn)

        scroll = ttk.Scrollbar(table_card)
        scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(table_card, columns=("date", "title", "category", "amount", "frequency", "source", "status", "select"), show="headings", yscrollcommand=scroll.set)
        scroll.config(command=self.tree.yview)

        self.tree.heading("date", text="Date")
        self.tree.heading("title", text="Merchant / Description")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount (₹)")
        self.tree.heading("frequency", text="Frequency")
        self.tree.heading("source", text="Method")
        self.tree.heading("status", text="Status")
        self.tree.heading("select", text="[ ✓ ]")

        self.tree.column("date", width=95, anchor="center")
        self.tree.column("title", width=220, anchor="w")
        self.tree.column("category", width=120, anchor="center")
        self.tree.column("amount", width=110, anchor="e")
        self.tree.column("frequency", width=95, anchor="center")
        self.tree.column("source", width=110, anchor="center")
        self.tree.column("status", width=95, anchor="center")
        self.tree.column("select", width=65, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.tag_configure("pending", foreground="#EF4444")
        self.tree.tag_configure("paid", foreground="#22C55E")

        self.tree.bind("<Button-1>", self.handle_tree_click)

        table_actions = tk.Frame(table_card, bg=self.colors["card_bg"])
        table_actions.pack(fill="x", padx=10, pady=(0, 10))

        self.select_all_var = tk.BooleanVar(value=False)
        select_all_btn = ttk.Checkbutton(table_actions, text="Select All", variable=self.select_all_var,
                                         command=self.toggle_select_all, style="Dark.TCheckbutton")
        select_all_btn.pack(side="left", padx=5)

        del_btn = tk.Button(table_actions, text="🗑️ Delete Selected", font=("Segoe UI", 9, "bold"),
                            bg=self.colors["accent_red"], fg="white", bd=0, cursor="hand2",
                            padx=10, pady=4, command=self.delete_selected_transactions)
        del_btn.pack(side="right", padx=(5, 0))

        edit_btn = tk.Button(table_actions, text="✏️ Edit Selected", font=("Segoe UI", 9, "bold"),
                             bg=self.colors["accent_yellow"], fg="#0F172A", bd=0, cursor="hand2",
                             padx=10, pady=4, command=self.edit_selected_transaction)
        edit_btn.pack(side="right", padx=5)

    def load_sample_sms(self, event):
        sel = self.sample_combobox.get()
        if sel != "Select sample notification...":
            self.upi_sms_entry.delete(0, tk.END)
            self.upi_sms_entry.insert(0, sel)

    def set_filter(self, f_name):
        self.active_filter = f_name
        for fn in ["All", "Subscription", "EMI", "Utility", "Current Month"]:
            btn = getattr(self, f"filter_btn_{fn.lower()}", None)
            if btn:
                if fn == f_name:
                    btn.config(bg=self.colors["accent_blue"], fg="#0F172A")
                else:
                    btn.config(bg=self.colors["card_border"], fg="white")
        self.refresh_ui()

    def filter_current_month_transactions(self):
        self.active_filter = "Current Month"
        self.refresh_ui()

    def open_calendar_picker(self):
        curr_val = self.date_entry.get().strip()
        dialog = CalendarDialog(self.root, initial_date=curr_val, colors=self.colors)
        self.root.wait_window(dialog)
        if dialog.result_date:
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, dialog.result_date)

    def create_stat_card(self, parent, title, initial_val, subtitle):
        card = tk.Frame(parent, bg=self.colors["card_bg"], highlightbackground=self.colors["card_border"], highlightthickness=1)
        lbl_title = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg=self.colors["text_secondary"], bg=self.colors["card_bg"])
        lbl_title.pack(anchor="w", padx=15, pady=(10, 2))
        lbl_val = tk.Label(card, text=initial_val, font=("Segoe UI", 16, "bold"), fg=self.colors["text_primary"], bg=self.colors["card_bg"])
        lbl_val.pack(anchor="w", padx=15, pady=(0, 2))
        lbl_sub = tk.Label(card, text=subtitle, font=("Segoe UI", 8), fg=self.colors["text_secondary"], bg=self.colors["card_bg"])
        lbl_sub.pack(anchor="w", padx=15, pady=(0, 10))
        card.val_label = lbl_val
        return card

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    for item in data:
                        if "status" not in item:
                            item["status"] = "Pending" if item.get("category") in ["Bills & Utilities", "Utility"] else "Paid"
                        if "frequency" not in item:
                            item["frequency"] = "Monthly"
                        if "recurring" not in item:
                            item["recurring"] = item.get("frequency") != "One-Time"
                        if "selected" not in item:
                            item["selected"] = False
                    return data
            except Exception:
                return []
        return []

    def save_data(self):
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.transactions, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

    def parse_upi_sms(self):
        sms_text = self.upi_sms_entry.get().strip()
        if not sms_text:
            messagebox.showwarning("Empty Payload", "Please enter a simulated SMS string.")
            return
        amount_match = re.search(r'(?:INR|Rs\.?|₹)\s*([\d,]+\.?\d*)', sms_text, re.IGNORECASE)
        to_match = re.search(r'(?:to|from)\s+([A-Za-z0-9\s]+?)\s+(?:via|Ref|on|Utility|\d)', sms_text, re.IGNORECASE)
        is_debit = "debit" in sms_text.lower() and "bill generated" not in sms_text.lower()
        if amount_match:
            amount = float(amount_match.group(1).replace(',', ''))
            merchant = to_match.group(1).strip() if to_match else "UPI Merchant"
            category = "Subscription"
            merchant_upper = merchant.upper()
            if any(k in merchant_upper for k in ["SWIGGY", "ZOMATO", "CAFE", "RESTO"]):
                category = "Food & Dining"
            elif any(k in merchant_upper for k in ["BLINKIT", "ZEPTO", "GROCERY"]):
                category = "Groceries"
            elif any(k in merchant_upper for k in ["NETFLIX", "SPOTIFY", "PRIME"]):
                category = "Subscription"
            elif any(k in merchant_upper for k in ["BESCOM", "ELECTRICITY", "WATER", "AIRTEL", "JIO", "BILL", "UTILITY"]):
                category = "Utility"
            elif any(k in merchant_upper for k in ["EMI", "LOAN", "FINANCE"]):
                category = "EMI"
            
            auto_updated_pending = False
            if is_debit:
                for txn in self.transactions:
                    if txn.get("status") == "Pending":
                        same_cat = (txn.get("category") == category)
                        title_match = (merchant_upper in txn.get("title", "").upper() or txn.get("title", "").upper() in merchant_upper)
                        if same_cat or title_match:
                            txn["status"] = "Paid"
                            auto_updated_pending = True
                            break
            
            status = "Pending" if (category == "Utility" and not is_debit) else ("Paid" if is_debit else "Pending")
            today_date = datetime.date.today().strftime("%Y-%m-%d")
            new_txn = {
                "date": today_date,
                "title": merchant,
                "category": category,
                "amount": amount,
                "frequency": "Monthly",
                "source": "UPI Autopay",
                "status": status,
                "recurring": True,
                "selected": False
            }
            self.transactions.insert(0, new_txn)
            self.save_data()
            self.refresh_ui()
            msg = f"Intercepted Payment Entry:\n• Payee: {merchant}\n• Amount: ₹{amount:,.2f}\n• Status: {status}"
            if auto_updated_pending:
                msg += "\n\n⚡ Automatically updated matching 'Pending' bill to 'Paid'!"
            messagebox.showinfo("⚡ Auto-Captured!", msg)
        else:
            messagebox.showerror("Parsing Error", "Could not parse amount from SMS. Ensure format contains 'INR <amount>'.")

    def add_transaction(self):
        date_str = self.date_entry.get().strip()
        title = self.title_entry.get().strip()
        category = self.category_combobox.get()
        amount_str = self.amount_entry.get().strip()
        payment_type = self.type_combobox.get()
        frequency = self.frequency_combobox.get()
        if not title:
            messagebox.showerror("Error", "Please enter a payee title.")
            return
        try:
            amount = float(amount_str)
            if amount <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount.")
            return
        status = "Pending" if category in ["Utility", "Bills & Utilities"] else "Paid"
        is_recurring = frequency != "One-Time"
        new_txn = {
            "date": date_str,
            "title": title,
            "category": category,
            "amount": amount,
            "frequency": frequency,
            "source": payment_type,
            "status": status,
            "recurring": is_recurring,
            "selected": False
        }
        self.transactions.insert(0, new_txn)
        self.save_data()
        self.reset_entry_form()
        self.refresh_ui()
        messagebox.showinfo("Success", "Payment entry added successfully!")

    def edit_transaction_by_index(self, idx):
        if 0 <= idx < len(self.transactions):
            item = self.transactions[idx]
            dialog = EditTransactionDialog(self.root, item, colors=self.colors)
            self.root.wait_window(dialog)
            if dialog.updated_data:
                self.transactions[idx] = dialog.updated_data
                self.save_data()
                self.refresh_ui()
                messagebox.showinfo("Success", "Payment entry updated successfully!")

    def edit_selected_transaction(self):
        selected_indices = [i for i, t in enumerate(self.transactions) if t.get("selected", False)]
        if not selected_indices:
            tree_sel = self.tree.selection()
            if tree_sel:
                filtered = self.get_filtered_transactions()
                idx_v = self.tree.index(tree_sel[0])
                if 0 <= idx_v < len(filtered):
                    selected_indices = [self.transactions.index(filtered[idx_v])]
        if not selected_indices:
            messagebox.showwarning("Warning", "Select a payment checkbox or row to edit.")
            return
        self.edit_transaction_by_index(selected_indices[0])

    def reset_entry_form(self):
        self.title_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.category_combobox.set("Subscription")
        self.type_combobox.set("UPI Autopay")
        self.frequency_combobox.set("Monthly")

    def toggle_select_all(self):
        state = self.select_all_var.get()
        for txn in self.transactions:
            txn["selected"] = state
        self.save_data()
        self.refresh_ui()

    def handle_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            col = self.tree.identify_column(event.x)
            row_id = self.tree.identify_row(event.y)
            if row_id:
                idx_in_view = self.tree.index(row_id)
                filtered_transactions = self.get_filtered_transactions()
                if 0 <= idx_in_view < len(filtered_transactions):
                    actual_txn = filtered_transactions[idx_in_view]
                    if col == "#7":
                        current_status = actual_txn.get("status", "Paid")
                        actual_txn["status"] = "Pending" if current_status == "Paid" else "Paid"
                        self.save_data()
                        self.refresh_ui()
                    elif col == "#8":
                        actual_txn["selected"] = not actual_txn.get("selected", False)
                        self.save_data()
                        self.refresh_ui()

    def delete_selected_transactions(self):
        selected_indices = [i for i, t in enumerate(self.transactions) if t.get("selected", False)]
        if not selected_indices:
            tree_sel = self.tree.selection()
            if tree_sel:
                for s in tree_sel:
                    filtered = self.get_filtered_transactions()
                    idx_v = self.tree.index(s)
                    if 0 <= idx_v < len(filtered):
                        selected_indices.append(self.transactions.index(filtered[idx_v]))
        if not selected_indices:
            messagebox.showwarning("Warning", "Select payment checkboxes to delete.")
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected_indices)} payment transaction(s)?"):
            self.transactions = [t for i, t in enumerate(self.transactions) if i not in selected_indices]
            self.save_data()
            self.refresh_ui()

    def get_filtered_transactions(self):
        if self.active_filter == "All":
            return self.transactions
        elif self.active_filter == "Current Month":
            curr_ym = datetime.date.today().strftime("%Y-%m")
            return [t for t in self.transactions if t.get("date", "").startswith(curr_ym)]
        return [t for t in self.transactions if t.get("category") == self.active_filter]

    def update_health_banner(self):
        pending_bills = [t for t in self.transactions if t.get("status") == "Pending"]
        subscriptions = [t for t in self.transactions if t.get("category") == "Subscription"]
        
        today = datetime.date.today()
        curr_ym = today.strftime("%Y-%m")
        first_day_curr = today.replace(day=1)
        prev_ym = (first_day_curr - datetime.timedelta(days=1)).strftime("%Y-%m")
        
        curr_month_exp = sum(t.get("amount", 0) for t in self.transactions if t.get("date", "").startswith(curr_ym))
        prev_month_exp = sum(t.get("amount", 0) for t in self.transactions if t.get("date", "").startswith(prev_ym))
        
        exceeded_80_percent = False
        if prev_month_exp > 0:
            limit_val = 0.8 * prev_month_exp
            if curr_month_exp > limit_val:
                exceeded_80_percent = True

        if self.banner_timer_id:
            try:
                self.root.after_cancel(self.banner_timer_id)
            except Exception:
                pass
            self.banner_timer_id = None

        new_alerts = []
        if pending_bills:
            new_alerts.append("pending_bills")
        if exceeded_80_percent:
            new_alerts.append("high_spending")
        if len(subscriptions) > 1:
            new_alerts.append("redundant_subs")
            
        if not new_alerts:
            new_alerts.append("success")

        if new_alerts != self.active_alerts_list:
            self.active_alerts_list = new_alerts
            self.current_alert_index = 0
        else:
            if self.current_alert_index >= len(self.active_alerts_list):
                self.current_alert_index = 0

        current_type = self.active_alerts_list[self.current_alert_index]
        self._render_single_banner(current_type, pending_bills, curr_month_exp, prev_month_exp)

        if len(self.active_alerts_list) > 1:
            self.current_alert_index = (self.current_alert_index + 1) % len(self.active_alerts_list)
            self.banner_timer_id = self.root.after(4000, self.update_health_banner)

    def _render_single_banner(self, alert_type, pending_bills, curr_month_exp, prev_month_exp):
        banner_top = self.banner_title.master

        if alert_type == "pending_bills":
            total_pending_amt = sum(b.get("amount", 0) for b in pending_bills)
            self.banner_card.config(bg="#7F1D1D", highlightbackground="#DC2626")
            banner_top.config(bg="#7F1D1D")
            self.banner_title.config(text=f"🚨 Bill Payment Alert: {len(pending_bills)} Pending Bill(s)", bg="#7F1D1D", fg="#FCA5A5")
            self.banner_desc.config(text=f"Action required! You have pending payments totaling ₹{total_pending_amt:,.2f} awaiting clearance.", bg="#7F1D1D", fg="#FECACA")
            self.banner_action_btn.pack_forget()

        elif alert_type == "high_spending":
            self.banner_card.config(bg="#581C87", highlightbackground="#7E22CE")
            banner_top.config(bg="#581C87")
            self.banner_title.config(text="🟣 High Spending Warning: 80% Threshold Exceeded", bg="#581C87", fg="#E9D5FF")
            self.banner_desc.config(text=f"Current month expenses (₹{curr_month_exp:,.2f}) crossed 80% of last month baseline (₹{prev_month_exp:,.2f}). Watch transactions over limit below!", bg="#581C87", fg="#F3E8FF")
            self.banner_action_btn.config(
                text="👁️ Watch Transactions", bg="#7E22CE", fg="white", activebackground="#6B21A8",
                command=self.filter_current_month_transactions
            )
            self.banner_action_btn.pack(side="right")

        elif alert_type == "redundant_subs":
            self.banner_card.config(bg="#9A3412", highlightbackground="#EA580C")
            banner_top.config(bg="#9A3412")
            self.banner_title.config(text="🟠 Redundant Subscription Warning", bg="#9A3412", fg="#FFEDD5")
            self.banner_desc.config(text="You have multiple active subscriptions in similar service categories. Review active subscriptions below!", bg="#9A3412", fg="#FED7AA")
            self.banner_action_btn.config(
                text="🔍 Review Subscriptions", bg="#EA580C", fg="white", activebackground="#C2410C",
                command=lambda: self.set_filter("Subscription")
            )
            self.banner_action_btn.pack(side="right")

        elif alert_type == "success":
            total_committed = sum(
                t.get("amount", 0) if t.get("frequency", "Monthly") == "Monthly"
                else t.get("amount", 0) / 12 if t.get("frequency") == "Annually"
                else 0 for t in self.transactions
            )
            self.banner_card.config(bg="#064E3B", highlightbackground="#059669")
            banner_top.config(bg="#064E3B")
            self.banner_title.config(text="✅ Financial Health: Looking Great!", bg="#064E3B", fg="#34D399")
            self.banner_desc.config(text=f"You are doing well! Committed Monthly Spend: ₹{total_committed:,.2f} | Active Scheduled Payments: {len(self.transactions)} | Pending Bills: None.", bg="#064E3B", fg="#A7F3D0")
            self.banner_action_btn.pack_forget()

    def refresh_ui(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        filtered = self.get_filtered_transactions()
        for item in filtered:
            status = item.get("status", "Paid")
            tag_name = "pending" if status == "Pending" else "paid"
            freq = item.get("frequency", "Monthly")
            freq_icon = f"🔁 {freq}" if freq != "One-Time" else "One-Time"
            chk_icon = "[ ✓ ]" if item.get("selected", False) else "[   ]"
            self.tree.insert("", "end", values=(
                item.get("date", "N/A"),
                item.get("title", "N/A"),
                item.get("category", "Other"),
                f"₹{item.get('amount', 0):,.2f}",
                freq_icon,
                item.get("source", "UPI Autopay"),
                status,
                chk_icon
            ), tags=(tag_name,))
        
        total_committed = sum(
            item.get("amount", 0) if item.get("frequency", "Monthly") == "Monthly"
            else item.get("amount", 0) / 12 if item.get("frequency") == "Annually"
            else 0
            for item in self.transactions
        )
        emis_total = sum(
            item.get("amount", 0) if item.get("frequency", "Monthly") == "Monthly"
            else item.get("amount", 0) / 12 if item.get("frequency") == "Annually"
            else 0
            for item in self.transactions if item.get("category") == "EMI"
        )
        pending_count = sum(1 for item in self.transactions if item.get("status") == "Pending")
        total_payments = len(self.transactions)
        
        self.card_committed.val_label.config(text=f"₹{total_committed:,.0f}")
        self.card_emis.val_label.config(text=f"₹{emis_total:,.0f}")
        self.card_due.val_label.config(text=f"{pending_count} Bills")
        self.card_mandates.val_label.config(text=f"{total_payments} Total")

        self.update_health_banner()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernFinPulseApp(root)
    root.mainloop()