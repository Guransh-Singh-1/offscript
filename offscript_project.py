import json
import os
import re
import datetime
import calendar
import csv
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CalendarDialog(tk.Toplevel):
    def __init__(self, parent, initial_date=None, colors=None):
        super().__init__(parent)
        self.title("Select Date")
        self.geometry("340x380")
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
        w = 340
        h = 380
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
        header = tk.Frame(self, bg=self.colors["card_bg"], pady=12)
        header.pack(fill="x")
        prev_btn = tk.Button(header, text="◄", font=("Segoe UI", 11, "bold"),
                             fg=self.colors["accent_blue"], bg=self.colors["card_bg"],
                             bd=0, activebackground=self.colors["card_bg"],
                             activeforeground="#0284C7", cursor="hand2", command=self.prev_month)
        prev_btn.pack(side="left", padx=15)
        self.month_lbl = tk.Label(header, font=("Segoe UI", 12, "bold"),
                                  fg=self.colors["text_primary"], bg=self.colors["card_bg"])
        self.month_lbl.pack(side="left", expand=True)
        next_btn = tk.Button(header, text="►", font=("Segoe UI", 11, "bold"),
                             fg=self.colors["accent_blue"], bg=self.colors["card_bg"],
                             bd=0, activebackground=self.colors["card_bg"],
                             activeforeground="#0284C7", cursor="hand2", command=self.next_month)
        next_btn.pack(side="right", padx=15)
        days_frame = tk.Frame(self, bg=self.colors["bg"], pady=8)
        days_frame.pack(fill="x", padx=10)
        for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            lbl = tk.Label(days_frame, text=day, width=4, font=("Segoe UI", 10, "bold"),
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
                    lbl.grid(row=row_idx, column=col_idx, padx=3, pady=3)
                else:
                    is_selected = (day == self.selected_day and 
                                   self.curr_month == self.selected_month and 
                                   self.curr_year == self.selected_year)
                    bg_color = self.colors["accent_blue"] if is_selected else self.colors["card_bg"]
                    fg_color = "#0F172A" if is_selected else self.colors["text_primary"]
                    btn = tk.Button(self.grid_frame, text=str(day), width=4, font=("Segoe UI", 10, "bold" if is_selected else "normal"),
                                    bg=bg_color, fg=fg_color, bd=0, cursor="hand2",
                                    activebackground=self.colors["accent_blue"],
                                    command=lambda d=day: self.select_day(d))
                    btn.grid(row=row_idx, column=col_idx, padx=3, pady=3)

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
        self.title("Edit Financial Entry")
        self.geometry("440x520")
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
        w = 440
        h = 520
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.transaction = transaction
        self.updated_data = None
        self.build_ui()

    def build_ui(self):
        container = tk.Frame(self, bg=self.colors["card_bg"], bd=1, relief="solid", highlightbackground=self.colors["accent_yellow"])
        container.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(container, text="✏️ Edit Financial Entry", font=("Segoe UI", 12, "bold"), fg=self.colors["accent_yellow"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(15, 10))

        tk.Label(container, text="Type:", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(2, 0))
        self.type_combobox = ttk.Combobox(container, values=["Expense", "Income"], font=("Segoe UI", 10), state="readonly")
        self.type_combobox.pack(fill="x", padx=15, pady=3, ipady=4)
        self.type_combobox.set(self.transaction.get("type", "Expense"))

        tk.Label(container, text="Payee / Source Name:", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(4, 0))
        self.title_entry = tk.Entry(container, font=("Segoe UI", 10), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.title_entry.pack(fill="x", padx=15, pady=3, ipady=4)
        self.title_entry.insert(0, self.transaction.get("title", ""))

        tk.Label(container, text="Amount in ₹:", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(4, 0))
        self.amount_entry = tk.Entry(container, font=("Segoe UI", 10), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.amount_entry.pack(fill="x", padx=15, pady=3, ipady=4)
        self.amount_entry.insert(0, str(self.transaction.get("amount", "")))

        tk.Label(container, text="Date (yyyy-mm-dd):", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(4, 0))
        date_frame = tk.Frame(container, bg=self.colors["card_bg"])
        date_frame.pack(fill="x", padx=15, pady=3)
        self.date_entry = tk.Entry(date_frame, font=("Segoe UI", 10), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.date_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.date_entry.insert(0, self.transaction.get("date", datetime.date.today().strftime("%Y-%m-%d")))
        cal_btn = tk.Button(date_frame, text="📅", font=("Segoe UI", 8), bg=self.colors["accent_blue"], fg="#0F172A", bd=0, cursor="hand2", command=self.open_calendar)
        cal_btn.pack(side="right", padx=(5, 0), ipady=3, ipadx=5)

        tk.Label(container, text="Category:", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(4, 0))
        self.category_combobox = ttk.Combobox(container, values=["Subscription", "EMI", "Utility", "Food & Dining", "Groceries", "Transport", "Salary", "Freelance", "Investment", "Other"], font=("Segoe UI", 10), state="readonly")
        self.category_combobox.pack(fill="x", padx=15, pady=3, ipady=3)
        self.category_combobox.set(self.transaction.get("category", "Subscription"))

        tk.Label(container, text="Payment Method & Billing Frequency:", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(4, 0))
        row_freq = tk.Frame(container, bg=self.colors["card_bg"])
        row_freq.pack(fill="x", padx=15, pady=3)
        self.method_combobox = ttk.Combobox(row_freq, values=["UPI Autopay", "Card Autopay", "Bank Standing Instruction", "Direct Credit", "Cash"], font=("Segoe UI", 10), state="readonly")
        self.method_combobox.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=3)
        self.method_combobox.set(self.transaction.get("source", "UPI Autopay"))

        self.frequency_combobox = ttk.Combobox(row_freq, values=["Monthly", "Annually", "One-Time"], font=("Segoe UI", 10), state="readonly")
        self.frequency_combobox.pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=3)
        self.frequency_combobox.set(self.transaction.get("frequency", "Monthly"))

        btn_frame = tk.Frame(container, bg=self.colors["card_bg"])
        btn_frame.pack(fill="x", padx=15, pady=(15, 10))

        save_btn = tk.Button(btn_frame, text="💾 Save Changes", font=("Segoe UI", 11, "bold"), bg=self.colors["accent_yellow"], fg="#0F172A", bd=0, cursor="hand2", command=self.save)
        save_btn.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=6)

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 11), bg=self.colors["card_border"], fg="white", bd=0, cursor="hand2", command=self.destroy)
        cancel_btn.pack(side="right", fill="x", expand=True, padx=(5, 0), ipady=6)

    def open_calendar(self):
        dialog = CalendarDialog(self, initial_date=self.date_entry.get().strip(), colors=self.colors)
        self.wait_window(dialog)
        if dialog.result_date:
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, dialog.result_date)

    def save(self):
        entry_type = self.type_combobox.get()
        title = self.title_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        date_str = self.date_entry.get().strip()
        category = self.category_combobox.get()
        payment_type = self.method_combobox.get()
        frequency = self.frequency_combobox.get()

        if not title:
            messagebox.showerror("Error", "Please enter a title or payee.")
            return
        try:
            amount = float(amount_str)
            if amount <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount.")
            return

        status = "Pending" if (entry_type == "Expense" and category in ["Utility", "Bills & Utilities"]) else self.transaction.get("status", "Paid")
        is_recurring = frequency != "One-Time"

        self.updated_data = {
            "type": entry_type,
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

class MultiFilterDialog(tk.Toplevel):
    def __init__(self, parent, available_categories, active_categories, start_date="", end_date="", colors=None):
        super().__init__(parent)
        self.title("Filter Transactions")
        self.geometry("380x520")
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
        w = 380
        h = 520
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.available_categories = available_categories
        self.selected_categories = list(active_categories)
        self.start_date = start_date
        self.end_date = end_date
        self.vars = {}
        self.build_ui()

    def build_ui(self):
        container = tk.Frame(self, bg=self.colors["card_bg"], bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        container.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(container, text="🔍 Filter Transactions", font=("Segoe UI", 12, "bold"), fg=self.colors["accent_blue"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(15, 5))
        
        tk.Label(container, text="Date Range (yyyy-mm-dd):", font=("Segoe UI", 10, "bold"), fg=self.colors["text_primary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(5, 2))
        
        date_box1 = tk.Frame(container, bg=self.colors["card_bg"])
        date_box1.pack(fill="x", padx=15, pady=2)
        tk.Label(date_box1, text="From:", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(side="left", padx=(0, 5))
        self.start_entry = tk.Entry(date_box1, font=("Segoe UI", 9), bg=self.colors["bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.start_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.start_entry.insert(0, self.start_date)
        start_cal = tk.Button(date_box1, text="📅", font=("Segoe UI", 8), bg=self.colors["accent_blue"], fg="#0F172A", bd=0, cursor="hand2", command=lambda: self.pick_date(self.start_entry))
        start_cal.pack(side="left", padx=(5, 0), ipady=3, ipadx=4)

        date_box2 = tk.Frame(container, bg=self.colors["card_bg"])
        date_box2.pack(fill="x", padx=15, pady=4)
        tk.Label(date_box2, text="To:    ", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(side="left", padx=(0, 5))
        self.end_entry = tk.Entry(date_box2, font=("Segoe UI", 9), bg=self.colors["bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.end_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.end_entry.insert(0, self.end_date)
        end_cal = tk.Button(date_box2, text="📅", font=("Segoe UI", 8), bg=self.colors["accent_blue"], fg="#0F172A", bd=0, cursor="hand2", command=lambda: self.pick_date(self.end_entry))
        end_cal.pack(side="left", padx=(5, 0), ipady=3, ipadx=4)

        tk.Label(container, text="Filter by Categories:", font=("Segoe UI", 10, "bold"), fg=self.colors["text_primary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(10, 2))

        cat_frame = tk.Frame(container, bg=self.colors["card_bg"])
        cat_frame.pack(fill="both", expand=True, padx=15, pady=2)

        for cat in self.available_categories:
            var = tk.BooleanVar(value=(cat in self.selected_categories))
            self.vars[cat] = var
            chk = ttk.Checkbutton(cat_frame, text=f"  {cat}", variable=var, style="Dark.TCheckbutton")
            chk.pack(anchor="w", pady=2)

        btn_frame = tk.Frame(container, bg=self.colors["card_bg"])
        btn_frame.pack(fill="x", padx=15, pady=(10, 15))

        apply_btn = tk.Button(btn_frame, text="Apply Filters", font=("Segoe UI", 10, "bold"), bg=self.colors["accent_blue"], fg="#0F172A", bd=0, cursor="hand2", command=self.apply)
        apply_btn.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=6)

        reset_btn = tk.Button(btn_frame, text="Reset All", font=("Segoe UI", 10), bg=self.colors["card_border"], fg="white", bd=0, cursor="hand2", command=self.reset_all)
        reset_btn.pack(side="right", fill="x", expand=True, padx=(5, 0), ipady=6)

    def pick_date(self, entry_widget):
        dialog = CalendarDialog(self, initial_date=entry_widget.get().strip(), colors=self.colors)
        self.wait_window(dialog)
        if dialog.result_date:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, dialog.result_date)

    def apply(self):
        self.selected_categories = [cat for cat, var in self.vars.items() if var.get()]
        self.start_date = self.start_entry.get().strip()
        self.end_date = self.end_entry.get().strip()
        self.destroy()

    def reset_all(self):
        for var in self.vars.values():
            var.set(False)
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)
        self.selected_categories = []
        self.start_date = ""
        self.end_date = ""

class ModernFinPulseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FinPulse — Unified Recurring Spend Tracker & Subscription Killer")
        self.root.geometry("1400x900")
        self.root.minsize(1150, 780)
        self.root.configure(bg="#0F172A")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(script_dir, "finpulse_data.json")
        self.users_file = os.path.join(script_dir, "finpulse_users.json")
        
        self.current_user = None
        self.auth_mode = "login"
        self.users = self.load_users()
        self.transactions = []
        self.budgets = {}
        self.auto_export_settings = {"enabled": False, "day": 1, "last_exported_month": ""}
        self.active_page = "Home"
        self.active_categories = []
        self.filter_start_date = ""
        self.filter_end_date = ""
        
        self.available_categories = ["Subscription", "EMI", "Utility", "Food & Dining", "Groceries", "Transport", "Salary", "Freelance", "Investment", "Other"]

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
            "input_bg": "#0F172A"
        }
        self.apply_ttk_styles()
        self.show_auth_screen()

    def load_users(self):
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_users(self):
        try:
            with open(self.users_file, "w") as f:
                json.dump(self.users, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save user data: {e}")

    def show_auth_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        auth_bg = tk.Frame(self.root, bg="#0B0F19")
        auth_bg.pack(fill="both", expand=True)

        card = tk.Frame(auth_bg, bg="#1E293B", bd=1, relief="solid", highlightbackground="#334155")
        card.place(relx=0.5, rely=0.5, anchor="center", width=440, height=540)

        tk.Label(card, text="FinPulse", font=("Segoe UI", 28, "bold"), fg="#38BDF8", bg="#1E293B").pack(pady=(45, 5))
        tk.Label(card, text="Sign in to manage your finances", font=("Segoe UI", 10), fg="#94A3B8", bg="#1E293B").pack(pady=(0, 25))

        self.auth_title_lbl = tk.Label(card, text="Sign in with your FinPulse account", font=("Segoe UI", 11, "bold"), fg="#F8FAFC", bg="#1E293B")
        self.auth_title_lbl.pack(anchor="w", padx=40, pady=(0, 6))

        tk.Label(card, text="Username", font=("Segoe UI", 10), fg="#94A3B8", bg="#1E293B").pack(anchor="w", padx=40, pady=(2, 0))
        self.user_entry = tk.Entry(card, font=("Segoe UI", 11), bg="#0F172A", fg="#F8FAFC", insertbackground="white", bd=1, relief="solid")
        self.user_entry.pack(fill="x", padx=40, pady=5, ipady=8)

        tk.Label(card, text="Password", font=("Segoe UI", 10), fg="#94A3B8", bg="#1E293B").pack(anchor="w", padx=40, pady=(8, 0))
        self.pass_entry = tk.Entry(card, font=("Segoe UI", 11), bg="#0F172A", fg="#F8FAFC", insertbackground="white", show="•", bd=1, relief="solid")
        self.pass_entry.pack(fill="x", padx=40, pady=5, ipady=8)

        self.auth_action_btn = tk.Button(card, text="Next", font=("Segoe UI", 11, "bold"), bg="#38BDF8", fg="#0F172A", activebackground="#0284C7", bd=0, cursor="hand2", command=self.handle_auth)
        self.auth_action_btn.pack(fill="x", padx=40, pady=(25, 15), ipady=10)

        self.toggle_auth_btn = tk.Button(card, text="Create account", font=("Segoe UI", 10, "bold"), fg="#38BDF8", bg="#1E293B", bd=0, cursor="hand2", activebackground="#1E293B", activeforeground="#0284C7", command=self.toggle_auth_mode)
        self.toggle_auth_btn.pack(pady=5)

    def toggle_auth_mode(self):
        if self.auth_mode == "login":
            self.auth_mode = "register"
            self.auth_title_lbl.config(text="Create your FinPulse account")
            self.auth_action_btn.config(text="Register")
            self.toggle_auth_btn.config(text="Sign in instead")
        else:
            self.auth_mode = "login"
            self.auth_title_lbl.config(text="Sign in with your FinPulse account")
            self.auth_action_btn.config(text="Next")
            self.toggle_auth_btn.config(text="Create account")

    def handle_auth(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Required", "Please enter both username and password.")
            return

        if self.auth_mode == "register":
            if username in self.users:
                messagebox.showerror("Registration Error", "Username already exists. Please sign in.")
                return
            self.users[username] = password
            self.save_users()
            messagebox.showinfo("Success", f"Account created successfully! Welcome to FinPulse, {username}.")
            self.current_user = username
            self.load_data()
            self.build_layout()
            self.switch_page("Home")
        else:
            if username in self.users and self.users[username] == password:
                self.current_user = username
                messagebox.showinfo("Success", f"Welcome back, {username}!")
                self.load_data()
                self.build_layout()
                self.switch_page("Home")
            else:
                messagebox.showerror("Error", "Invalid username or password.")

    def apply_ttk_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#1E293B",
                        foreground="#F8FAFC",
                        fieldbackground="#1E293B",
                        rowheight=38,
                        font=("Segoe UI", 11),
                        borderwidth=0)
        style.map("Treeview", background=[("selected", "#38BDF8")], foreground=[("selected", "#0F172A")])
        style.configure("Treeview.Heading",
                        background="#334155",
                        foreground="#F8FAFC",
                        font=("Segoe UI", 11, "bold"),
                        borderwidth=0)
        style.configure("Dark.TCheckbutton",
                        background=self.colors["card_bg"],
                        foreground=self.colors["text_primary"],
                        font=("Segoe UI", 10))
        style.map("Dark.TCheckbutton",
                  background=[("active", self.colors["card_bg"])],
                  foreground=[("active", self.colors["text_primary"])])

    def build_layout(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_layout = tk.Frame(self.root, bg=self.colors["bg"])
        main_layout.pack(fill="both", expand=True)

        sidebar = tk.Frame(main_layout, bg=self.colors["sidebar_bg"], width=270)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand_frame = tk.Frame(sidebar, bg=self.colors["sidebar_bg"], pady=25, padx=20)
        brand_frame.pack(fill="x")
        tk.Label(brand_frame, text="FinPulse", font=("Segoe UI", 20, "bold"), fg=self.colors["text_primary"], bg=self.colors["sidebar_bg"]).pack(anchor="w")
        tk.Label(brand_frame, text="Financial Intelligence", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["sidebar_bg"]).pack(anchor="w")

        search_container = tk.Frame(sidebar, bg=self.colors["sidebar_bg"], padx=15, pady=8)
        search_container.pack(fill="x")
        search_box = tk.Entry(search_container, font=("Segoe UI", 10), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white", relief="solid", bd=1)
        search_box.pack(fill="x", ipady=6, ipadx=5)
        search_box.insert(0, "🔍 Quick search...")

        nav_frame = tk.Frame(sidebar, bg=self.colors["sidebar_bg"], pady=20, padx=10)
        nav_frame.pack(fill="x")

        nav_items = [
            ("🏠  Home", "Home"),
            ("📊  Visual Analytics & Budget", "Visual Analytics & Budget"),
            ("💳  All Transaction / filtering", "All Transaction / filtering"),
            ("📥  Export Data", "Export Data")
        ]

        for text, page_key in nav_items:
            btn = tk.Button(nav_frame, text=text, font=("Segoe UI", 10, "bold"), bg=self.colors["sidebar_bg"], fg=self.colors["text_secondary"], activebackground=self.colors["card_border"], activeforeground=self.colors["text_primary"], bd=0, anchor="w", padx=12, pady=12, cursor="hand2", command=lambda pk=page_key: self.switch_page(pk))
            btn.pack(fill="x", pady=5)

        bottom_sidebar = tk.Frame(sidebar, bg=self.colors["sidebar_bg"], padx=15, pady=20)
        bottom_sidebar.pack(side="bottom", fill="x")

        pro_card = tk.Frame(bottom_sidebar, bg="#111827", highlightbackground="#374151", highlightthickness=1, padx=14, pady=12)
        pro_card.pack(fill="x", pady=(0, 20))
        tk.Label(pro_card, text="⭐ Upgrade to Pro", font=("Segoe UI", 10, "bold"), fg=self.colors["accent_yellow"], bg="#111827").pack(anchor="w")
        tk.Label(pro_card, text="Unlock advanced AI limits & unlimited alerts.", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg="#111827", wraplength=200, justify="left").pack(anchor="w", pady=(3, 10))
        tk.Button(pro_card, text="Upgrade Now", font=("Segoe UI", 9, "bold"), bg=self.colors["accent_yellow"], fg="#0F172A", bd=0, cursor="hand2", padx=10, pady=6).pack(fill="x")

        user_card = tk.Frame(bottom_sidebar, bg=self.colors["sidebar_bg"])
        user_card.pack(fill="x")
        display_name = self.current_user if self.current_user else "User"
        tk.Label(user_card, text=f"👤  {display_name.upper()}", font=("Segoe UI", 10, "bold"), fg=self.colors["text_primary"], bg=self.colors["sidebar_bg"]).pack(side="left", anchor="w")
        
        logout_btn = tk.Button(user_card, text="🔒", font=("Segoe UI", 9), bg=self.colors["sidebar_bg"], fg=self.colors["text_secondary"], bd=0, cursor="hand2", command=self.show_auth_screen)
        logout_btn.pack(side="right")

        self.content_area = tk.Frame(main_layout, bg=self.colors["bg"])
        self.content_area.pack(side="right", fill="both", expand=True, padx=35, pady=25)

        self.check_auto_export_trigger()

    def switch_page(self, page_key):
        self.active_page = page_key
        for widget in self.content_area.winfo_children():
            widget.destroy()

        display_name = self.current_user if self.current_user else "User"

        top_bar = tk.Frame(self.content_area, bg=self.colors["bg"])
        top_bar.pack(fill="x", pady=(0, 25))

        title_frame = tk.Frame(top_bar, bg=self.colors["bg"])
        title_frame.pack(side="left")
        tk.Label(title_frame, text=f"Good morning, {display_name.upper()} 👋", font=("Segoe UI", 28, "bold"), fg=self.colors["text_primary"], bg=self.colors["bg"]).pack(anchor="w")
        tk.Label(title_frame, text="Financial Intelligence & Command Center", font=("Segoe UI", 12), fg=self.colors["text_secondary"], bg=self.colors["bg"]).pack(anchor="w", pady=(4, 0))

        live_badge = tk.Label(top_bar, text="● Live Engine Active", font=("Segoe UI", 11, "bold"), fg=self.colors["accent_green"], bg="#064E3B", padx=16, pady=10)
        live_badge.pack(side="right")

        if page_key == "Home":
            self.build_home_page()
        elif page_key == "Visual Analytics & Budget":
            self.build_visual_analytics_page()
        elif page_key == "All Transaction / filtering":
            self.build_transaction_filtering_page()
        elif page_key == "Export Data":
            self.build_export_page()

    def build_home_page(self):
        stats_frame = tk.Frame(self.content_area, bg=self.colors["bg"])
        stats_frame.pack(fill="x", pady=(0, 25))

        self.card_committed = self.create_stat_card(stats_frame, "COMMITTED MONTHLY", "₹0.00", "Pre-allocated before discretionary spend")
        self.card_committed.pack(side="left", fill="x", expand=True, padx=(0, 18))

        self.card_emis = self.create_stat_card(stats_frame, "MONTHLY EMIs", "₹0.00", "Total monthly debt obligations")
        self.card_emis.pack(side="left", fill="x", expand=True, padx=(0, 18))

        self.card_due = self.create_stat_card(stats_frame, "DUE IN 7 DAYS", "0 Bills", "Action required soon")
        self.card_due.pack(side="left", fill="x", expand=True, padx=(0, 18))

        self.card_mandates = self.create_stat_card(stats_frame, "ACTIVE PAYMENTS", "0 Total", "UPI Autopay & Card Mandates")
        self.card_mandates.pack(side="left", fill="x", expand=True)

        self.banner_card = tk.Frame(self.content_area, bg="#064E3B", highlightbackground="#059669", highlightthickness=1)
        self.banner_card.pack(fill="x", pady=(0, 25), ipady=18, ipadx=18)
        
        banner_top = tk.Frame(self.banner_card, bg="#064E3B")
        banner_top.pack(fill="x", padx=15, pady=(4, 0))

        self.banner_title = tk.Label(banner_top, text="✅ Financial Health: Looking Great!", font=("Segoe UI", 14, "bold"), fg="#34D399", bg="#064E3B")
        self.banner_title.pack(side="left", anchor="w")

        self.banner_action_btn = tk.Button(banner_top, text="", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", padx=12, pady=6)
        self.banner_action_btn.pack(side="right")
        self.banner_action_btn.pack_forget()

        self.banner_desc = tk.Label(self.banner_card, text="Analyzing active recurring transactions and financial health...", font=("Segoe UI", 11), fg="#A7F3D0", bg="#064E3B")
        self.banner_desc.pack(anchor="w", padx=15, pady=(6, 4))

        inputs_frame = tk.Frame(self.content_area, bg=self.colors["bg"])
        inputs_frame.pack(fill="both", expand=True, pady=(0, 10))
        inputs_frame.columnconfigure(0, weight=1)
        inputs_frame.columnconfigure(1, weight=1)
        inputs_frame.rowconfigure(0, weight=1)

        upi_card = tk.LabelFrame(inputs_frame, text=" Smart Bank / UPI SMS Ingestion ", font=("Segoe UI", 12, "bold"),
                                 bg=self.colors["card_bg"], fg=self.colors["accent_blue"],
                                 bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        upi_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)

        tk.Label(upi_card, text="Select sample notification or type custom message below:", font=("Segoe UI", 11), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=15, pady=(15, 8))
        
        self.sample_combobox = ttk.Combobox(upi_card, values=[
            "Select sample notification...",
            "A/c XX1234 debited by INR 649.00 on 2026-10-22 to NETFLIX via UPI Ref 928301",
            "A/c XX1234 bill generated for INR 1,450.00 on 2026-10-22 from BESCOM Utility due soon",
            "A/c XX1234 credited by INR 75,000.00 on 2026-10-22 salary credit via Direct Credit",
            "A/c XX1234 debited by INR 12,500.00 on 2026-10-22 to HDFC LOAN EMI via UPI Ref 928303"
        ], font=("Segoe UI", 11), state="readonly")
        self.sample_combobox.pack(fill="x", padx=15, pady=(0, 12), ipady=6)
        self.sample_combobox.set("Select sample notification...")
        self.sample_combobox.bind("<<ComboboxSelected>>", self.load_sample_sms)

        self.upi_sms_entry = tk.Entry(upi_card, font=("Segoe UI", 11), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white", bd=1, relief="solid")
        self.upi_sms_entry.pack(fill="x", padx=15, pady=8, ipady=10)
        self.upi_sms_entry.insert(0, "A/c XX1234 bill generated for INR 1,450.00 on 2026-10-22 from BESCOM Utility due soon")

        parse_btn = tk.Button(upi_card, text="Scan & Add Transaction", font=("Segoe UI", 12, "bold"),
                              bg=self.colors["accent_blue"], fg="#0F172A", activebackground="#0284C7",
                              bd=0, cursor="hand2", command=self.parse_upi_sms)
        parse_btn.pack(fill="x", padx=15, pady=(20, 15), ipady=12)

        self.manual_card = tk.LabelFrame(inputs_frame, text=" Add Financial Entry Manually ", font=("Segoe UI", 12, "bold"),
                                         bg=self.colors["card_bg"], fg=self.colors["text_primary"],
                                         bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        self.manual_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)

        form_grid = tk.Frame(self.manual_card, bg=self.colors["card_bg"])
        form_grid.pack(fill="x", padx=15, pady=8)

        r0_c0 = tk.Frame(form_grid, bg=self.colors["card_bg"])
        r0_c0.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(r0_c0, text="Type", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 0))
        self.type_combobox = ttk.Combobox(r0_c0, values=["Expense", "Income"], font=("Segoe UI", 10), state="readonly")
        self.type_combobox.pack(fill="x", pady=3, ipady=6)
        self.type_combobox.set("Expense")

        r0_c1 = tk.Frame(form_grid, bg=self.colors["card_bg"])
        r0_c1.pack(side="left", fill="x", expand=True, padx=6)
        tk.Label(r0_c1, text="Payee / Source", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 0))
        self.title_entry = tk.Entry(r0_c1, font=("Segoe UI", 10), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.title_entry.pack(fill="x", pady=3, ipady=6)

        r0_c2 = tk.Frame(form_grid, bg=self.colors["card_bg"])
        r0_c2.pack(side="left", fill="x", expand=True, padx=(6, 0))
        tk.Label(r0_c2, text="Amount in ₹", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 0))
        self.amount_entry = tk.Entry(r0_c2, font=("Segoe UI", 10), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.amount_entry.pack(fill="x", pady=3, ipady=6)

        form_grid2 = tk.Frame(self.manual_card, bg=self.colors["card_bg"])
        form_grid2.pack(fill="x", padx=15, pady=8)

        r1_c0 = tk.Frame(form_grid2, bg=self.colors["card_bg"])
        r1_c0.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(r1_c0, text="Date", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 0))
        date_box_frame = tk.Frame(r1_c0, bg=self.colors["card_bg"])
        date_box_frame.pack(fill="x", pady=3)
        self.date_entry = tk.Entry(date_box_frame, font=("Segoe UI", 10), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.date_entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        cal_btn = tk.Button(date_box_frame, text="📅", font=("Segoe UI", 9), bg=self.colors["accent_blue"], fg="#0F172A", bd=0, cursor="hand2", command=self.open_calendar_picker)
        cal_btn.pack(side="right", padx=(4, 0), ipady=5, ipadx=8)

        r1_c1 = tk.Frame(form_grid2, bg=self.colors["card_bg"])
        r1_c1.pack(side="left", fill="x", expand=True, padx=6)
        tk.Label(r1_c1, text="Category", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 0))
        self.category_combobox = ttk.Combobox(r1_c1, values=["Subscription", "EMI", "Utility", "Food & Dining", "Groceries", "Transport", "Salary", "Freelance", "Investment", "Other"], font=("Segoe UI", 10), state="readonly")
        self.category_combobox.pack(fill="x", pady=3, ipady=6)
        self.category_combobox.set("Utility")

        r1_c2 = tk.Frame(form_grid2, bg=self.colors["card_bg"])
        r1_c2.pack(side="left", fill="x", expand=True, padx=(6, 0))
        tk.Label(r1_c2, text="Method & Freq", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 0))
        self.frequency_combobox = ttk.Combobox(r1_c2, values=["Monthly", "Annually", "One-Time"], font=("Segoe UI", 10), state="readonly")
        self.frequency_combobox.pack(fill="x", pady=3, ipady=6)
        self.frequency_combobox.set("Monthly")

        form_grid3 = tk.Frame(self.manual_card, bg=self.colors["card_bg"])
        form_grid3.pack(fill="x", padx=15, pady=(12, 10))

        self.save_btn = tk.Button(form_grid3, text="+ Add Financial Entry", font=("Segoe UI", 11, "bold"),
                                  bg="#6366F1", fg="white", activebackground="#4F46E5",
                                  bd=0, cursor="hand2", command=self.add_transaction)
        self.save_btn.pack(side="left", fill="x", expand=True, ipady=10)

        self.refresh_ui()

    def build_visual_analytics_page(self):
        container = tk.Frame(self.content_area, bg=self.colors["bg"])
        container.pack(fill="both", expand=True)

        curr_ym = datetime.date.today().strftime("%Y-%m")
        curr_month_name = datetime.date.today().strftime("%B %Y")
        
        dashboard_card = tk.LabelFrame(container, text=f" Personal Finance Dashboard — {curr_month_name} ", font=("Segoe UI", 12, "bold"),
                                       bg=self.colors["card_bg"], fg=self.colors["accent_yellow"], bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        dashboard_card.pack(fill="x", pady=(0, 15), ipadx=15, ipady=10)

        metrics_frame = tk.Frame(dashboard_card, bg=self.colors["card_bg"])
        metrics_frame.pack(fill="x", padx=15, pady=10)

        curr_income, curr_expense, net_bal = self.calculate_monthly_finances(curr_ym)

        self.dash_income_lbl = self.create_metric_widget(metrics_frame, "CURRENT MONTH INCOME", f"₹{curr_income:,.2f}", self.colors["accent_green"])
        self.dash_income_lbl.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.dash_expense_lbl = self.create_metric_widget(metrics_frame, "CURRENT MONTH EXPENSE", f"₹{curr_expense:,.2f}", self.colors["accent_red"])
        self.dash_expense_lbl.pack(side="left", fill="x", expand=True, padx=(0, 10))

        net_color = self.colors["accent_blue"] if net_bal >= 0 else self.colors["accent_red"]
        self.dash_net_lbl = self.create_metric_widget(metrics_frame, "NET BALANCE", f"₹{net_bal:,.2f}", net_color)
        self.dash_net_lbl.pack(side="left", fill="x", expand=True, padx=(0, 10))

        budget_val = self.budgets.get(curr_ym, 0.0)
        budget_widget_frame = tk.Frame(metrics_frame, bg=self.colors["card_bg"])
        budget_widget_frame.pack(side="left", fill="x", expand=True)
        tk.Label(budget_widget_frame, text="MONTHLY BUDGET", font=("Segoe UI", 8, "bold"), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 2))
        
        b_input_box = tk.Frame(budget_widget_frame, bg=self.colors["card_bg"])
        b_input_box.pack(fill="x")
        self.budget_entry = tk.Entry(b_input_box, font=("Segoe UI", 10), bg=self.colors["bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.budget_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.budget_entry.insert(0, str(budget_val) if budget_val > 0 else "")
        set_b_btn = tk.Button(b_input_box, text="Set Budget", font=("Segoe UI", 9, "bold"), bg=self.colors["accent_blue"], fg="#0F172A", bd=0, cursor="hand2", command=self.save_monthly_budget)
        set_b_btn.pack(side="right", padx=(5, 0), ipadx=8, ipady=3)

        graphs_frame = tk.Frame(container, bg=self.colors["bg"])
        graphs_frame.pack(fill="both", expand=True, pady=(5, 0))
        graphs_frame.columnconfigure(0, weight=1)
        graphs_frame.columnconfigure(1, weight=1)
        graphs_frame.rowconfigure(0, weight=1)

        cat_card = tk.LabelFrame(graphs_frame, text=f" Expense Category Breakdown (Click Slice to View) — {curr_month_name} ", font=("Segoe UI", 11, "bold"),
                                 bg=self.colors["card_bg"], fg=self.colors["text_primary"], bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        cat_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        hist_card = tk.LabelFrame(graphs_frame, text=" Historical Monthly Total Expenses ", font=("Segoe UI", 11, "bold"),
                                  bg=self.colors["card_bg"], fg=self.colors["text_primary"], bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        hist_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.render_pie_chart(cat_card, curr_ym)
        self.render_line_graph(hist_card)

    def build_export_page(self):
        container = tk.Frame(self.content_area, bg=self.colors["bg"])
        container.pack(fill="both", expand=True)

        auto_card = tk.LabelFrame(container, text=" ⚙️ Automated Monthly CSV Backup ", font=("Segoe UI", 12, "bold"),
                                  bg=self.colors["card_bg"], fg=self.colors["accent_green"], bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        auto_card.pack(fill="x", pady=(0, 15), ipadx=15, ipady=12)

        auto_row = tk.Frame(auto_card, bg=self.colors["card_bg"])
        auto_row.pack(fill="x", padx=15, pady=8)

        self.auto_export_var = tk.BooleanVar(value=self.auto_export_settings.get("enabled", False))
        auto_chk = ttk.Checkbutton(auto_row, text=" Enable Monthly Auto-Export (CSV Backup)", variable=self.auto_export_var, style="Dark.TCheckbutton", command=self.save_auto_export_settings)
        auto_chk.pack(side="left", padx=(0, 20))

        tk.Label(auto_row, text="Trigger Day of Month:", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(side="left", padx=(10, 5))
        self.auto_day_combo = ttk.Combobox(auto_row, values=[str(i) for i in range(1, 29)], font=("Segoe UI", 10), state="readonly", width=5)
        self.auto_day_combo.pack(side="left", padx=(0, 10), ipady=3)
        self.auto_day_combo.set(str(self.auto_export_settings.get("day", 1)))
        self.auto_day_combo.bind("<<ComboboxSelected>>", lambda e: self.save_auto_export_settings())

        tk.Label(auto_row, text="(Overwrites old backup automatically)", font=("Segoe UI", 9, "italic"), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(side="left", padx=10)

        config_card = tk.LabelFrame(container, text=" 📥 Manual Export Transactions Setup ", font=("Segoe UI", 12, "bold"),
                                    bg=self.colors["card_bg"], fg=self.colors["accent_blue"], bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        config_card.pack(fill="x", pady=(0, 15), ipadx=15, ipady=15)

        row1 = tk.Frame(config_card, bg=self.colors["card_bg"])
        row1.pack(fill="x", padx=15, pady=5)

        f_start = tk.Frame(row1, bg=self.colors["card_bg"])
        f_start.pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Label(f_start, text="Start Date (yyyy-mm-dd):", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 2))
        s_box = tk.Frame(f_start, bg=self.colors["card_bg"])
        s_box.pack(fill="x")
        self.exp_start_entry = tk.Entry(s_box, font=("Segoe UI", 10), bg=self.colors["bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.exp_start_entry.pack(side="left", fill="x", expand=True, ipady=5)
        s_cal = tk.Button(s_box, text="📅", font=("Segoe UI", 9), bg=self.colors["accent_blue"], fg="#0F172A", bd=0, cursor="hand2", command=lambda: self.pick_export_date(self.exp_start_entry))
        s_cal.pack(side="right", padx=(5, 0), ipadx=6, ipady=4)

        f_end = tk.Frame(row1, bg=self.colors["card_bg"])
        f_end.pack(side="left", fill="x", expand=True, padx=(10, 10))
        tk.Label(f_end, text="End Date (yyyy-mm-dd):", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 2))
        e_box = tk.Frame(f_end, bg=self.colors["card_bg"])
        e_box.pack(fill="x")
        self.exp_end_entry = tk.Entry(e_box, font=("Segoe UI", 10), bg=self.colors["bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.exp_end_entry.pack(side="left", fill="x", expand=True, ipady=5)
        e_cal = tk.Button(e_box, text="📅", font=("Segoe UI", 9), bg=self.colors["accent_blue"], fg="#0F172A", bd=0, cursor="hand2", command=lambda: self.pick_export_date(self.exp_end_entry))
        e_cal.pack(side="right", padx=(5, 0), ipadx=6, ipady=4)

        f_type = tk.Frame(row1, bg=self.colors["card_bg"])
        f_type.pack(side="left", fill="x", expand=True, padx=(10, 0))
        tk.Label(f_type, text="Transaction Type:", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", pady=(2, 2))
        self.exp_type_combo = ttk.Combobox(f_type, values=["All Types", "Expense Only", "Income Only"], font=("Segoe UI", 10), state="readonly")
        self.exp_type_combo.pack(fill="x", ipady=5)
        self.exp_type_combo.set("All Types")
        self.exp_type_combo.bind("<<ComboboxSelected>>", lambda e: self.update_export_preview())

        presets_row = tk.Frame(config_card, bg=self.colors["card_bg"])
        presets_row.pack(fill="x", padx=15, pady=(10, 5))
        tk.Label(presets_row, text="Quick Presets:", font=("Segoe UI", 10, "bold"), fg=self.colors["text_primary"], bg=self.colors["card_bg"]).pack(side="left", padx=(0, 10))

        tk.Button(presets_row, text="All Time", font=("Segoe UI", 9), bg=self.colors["card_border"], fg="white", bd=0, cursor="hand2", command=lambda: self.set_export_preset("all")).pack(side="left", padx=4)
        tk.Button(presets_row, text="This Month", font=("Segoe UI", 9), bg=self.colors["card_border"], fg="white", bd=0, cursor="hand2", command=lambda: self.set_export_preset("this_month")).pack(side="left", padx=4)
        tk.Button(presets_row, text="Last 30 Days", font=("Segoe UI", 9), bg=self.colors["card_border"], fg="white", bd=0, cursor="hand2", command=lambda: self.set_export_preset("30_days")).pack(side="left", padx=4)
        tk.Button(presets_row, text="Last 90 Days", font=("Segoe UI", 9), bg=self.colors["card_border"], fg="white", bd=0, cursor="hand2", command=lambda: self.set_export_preset("90_days")).pack(side="left", padx=4)

        action_row = tk.Frame(config_card, bg=self.colors["card_bg"])
        action_row.pack(fill="x", padx=15, pady=(15, 0))

        tk.Label(action_row, text="Export Format:", font=("Segoe UI", 10, "bold"), fg=self.colors["text_primary"], bg=self.colors["card_bg"]).pack(side="left", padx=(0, 10))
        self.exp_format_combo = ttk.Combobox(action_row, values=["CSV (.csv)", "PDF Document (.pdf)", "JSON Data (.json)"], font=("Segoe UI", 10), state="readonly", width=22)
        self.exp_format_combo.pack(side="left", padx=(0, 20), ipady=4)
        self.exp_format_combo.set("CSV (.csv)")

        run_exp_btn = tk.Button(action_row, text="💾 Export File Now", font=("Segoe UI", 11, "bold"), bg=self.colors["accent_green"], fg="#0F172A", bd=0, cursor="hand2", padx=20, pady=8, command=self.execute_export)
        run_exp_btn.pack(side="left")

        preview_card = tk.LabelFrame(container, text=" Live Export Dataset Preview ", font=("Segoe UI", 12, "bold"),
                                    bg=self.colors["card_bg"], fg=self.colors["text_primary"], bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        preview_card.pack(fill="both", expand=True)

        prev_header = tk.Frame(preview_card, bg=self.colors["card_bg"])
        prev_header.pack(fill="x", padx=15, pady=8)
        self.exp_summary_lbl = tk.Label(prev_header, text="Records Found: 0 | Total Value: ₹0.00", font=("Segoe UI", 10, "bold"), fg=self.colors["accent_blue"], bg=self.colors["card_bg"])
        self.exp_summary_lbl.pack(side="left")

        scroll = ttk.Scrollbar(preview_card)
        scroll.pack(side="right", fill="y")

        self.exp_tree = ttk.Treeview(preview_card, columns=("date", "type", "title", "category", "amount", "frequency", "source", "status"), show="headings", yscrollcommand=scroll.set)
        scroll.config(command=self.exp_tree.yview)

        self.exp_tree.heading("date", text="Date")
        self.exp_tree.heading("type", text="Type")
        self.exp_tree.heading("title", text="Payee / Source")
        self.exp_tree.heading("category", text="Category")
        self.exp_tree.heading("amount", text="Amount (₹)")
        self.exp_tree.heading("frequency", text="Frequency")
        self.exp_tree.heading("source", text="Method")
        self.exp_tree.heading("status", text="Status")

        self.exp_tree.column("date", width=100, anchor="center")
        self.exp_tree.column("type", width=90, anchor="center")
        self.exp_tree.column("title", width=220, anchor="w")
        self.exp_tree.column("category", width=130, anchor="center")
        self.exp_tree.column("amount", width=120, anchor="e")
        self.exp_tree.column("frequency", width=105, anchor="center")
        self.exp_tree.column("source", width=120, anchor="center")
        self.exp_tree.column("status", width=95, anchor="center")

        self.exp_tree.pack(fill="both", expand=True, padx=15, pady=10)

        self.set_export_preset("all")

    def build_transaction_filtering_page(self):
        table_card = tk.LabelFrame(self.content_area, text=" All Transactions & Multi-Category Filtering ", font=("Segoe UI", 12, "bold"),
                                    bg=self.colors["card_bg"], fg=self.colors["text_primary"],
                                    bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        table_card.pack(fill="both", expand=True)

        table_header_frame = tk.Frame(table_card, bg=self.colors["card_bg"])
        table_header_frame.pack(fill="x", padx=15, pady=10)
        
        info_frame = tk.Frame(table_header_frame, bg=self.colors["card_bg"])
        info_frame.pack(side="left")
        
        tk.Label(info_frame, text="Filter and manage your full list of financial transactions:", font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w")

        filter_btn_frame = tk.Frame(table_header_frame, bg=self.colors["card_bg"])
        filter_btn_frame.pack(side="right")

        self.active_filters_lbl = tk.Label(filter_btn_frame, text="Showing All Transactions", font=("Segoe UI", 9, "bold"), fg=self.colors["accent_blue"], bg=self.colors["card_bg"])
        self.active_filters_lbl.pack(side="left", padx=(0, 10))

        self.clear_filter_btn = tk.Button(filter_btn_frame, text="✖ Clear", font=("Segoe UI", 9), fg=self.colors["accent_red"], bg=self.colors["card_bg"], bd=0, cursor="hand2", command=self.clear_filters)
        self.clear_filter_btn.pack(side="left", padx=(0, 10))
        self.clear_filter_btn.pack_forget()

        open_filter_dialog_btn = tk.Button(filter_btn_frame, text="🔍 Filter Options", font=("Segoe UI", 10, "bold"),
                                           bg=self.colors["accent_blue"], fg="#0F172A", bd=0, padx=14, pady=6, cursor="hand2",
                                           command=self.open_filter_dialog)
        open_filter_dialog_btn.pack(side="right")

        scroll = ttk.Scrollbar(table_card)
        scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(table_card, columns=("date", "type", "title", "category", "amount", "frequency", "source", "status", "select"), show="headings", yscrollcommand=scroll.set)
        scroll.config(command=self.tree.yview)

        self.tree.heading("date", text="Date")
        self.tree.heading("type", text="Type")
        self.tree.heading("title", text="Payee / Source")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount (₹)")
        self.tree.heading("frequency", text="Frequency")
        self.tree.heading("source", text="Method")
        self.tree.heading("status", text="Status")
        self.tree.heading("select", text="[ ✓ ]")

        self.tree.column("date", width=95, anchor="center")
        self.tree.column("type", width=85, anchor="center")
        self.tree.column("title", width=200, anchor="w")
        self.tree.column("category", width=120, anchor="center")
        self.tree.column("amount", width=110, anchor="e")
        self.tree.column("frequency", width=95, anchor="center")
        self.tree.column("source", width=110, anchor="center")
        self.tree.column("status", width=90, anchor="center")
        self.tree.column("select", width=65, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=15, pady=15)
        self.tree.tag_configure("pending", foreground="#EF4444")
        self.tree.tag_configure("paid", foreground="#22C55E")
        self.tree.tag_configure("income", foreground="#38BDF8")
        self.tree.bind("<Button-1>", self.handle_tree_click)

        table_actions = tk.Frame(table_card, bg=self.colors["card_bg"])
        table_actions.pack(fill="x", padx=15, pady=(0, 15))

        self.select_all_var = tk.BooleanVar(value=False)
        select_all_btn = ttk.Checkbutton(table_actions, text="Select All", variable=self.select_all_var,
                                         command=self.toggle_select_all, style="Dark.TCheckbutton")
        select_all_btn.pack(side="left", padx=5)

        del_btn = tk.Button(table_actions, text="🗑️ Delete Selected", font=("Segoe UI", 10, "bold"),
                            bg=self.colors["accent_red"], fg="white", bd=0, cursor="hand2",
                            padx=12, pady=6, command=self.delete_selected_transactions)
        del_btn.pack(side="right", padx=(6, 0))

        edit_btn = tk.Button(table_actions, text="✏️ Edit Selected", font=("Segoe UI", 10, "bold"),
                             bg=self.colors["accent_yellow"], fg="#0F172A", bd=0, cursor="hand2",
                             padx=12, pady=6, command=self.edit_selected_transaction)
        edit_btn.pack(side="right", padx=6)

        self.refresh_ui()

    def create_stat_card(self, parent, title, initial_val, subtitle):
        card = tk.Frame(parent, bg=self.colors["card_bg"], highlightbackground=self.colors["card_border"], highlightthickness=1)
        lbl_title = tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), fg=self.colors["text_secondary"], bg=self.colors["card_bg"])
        lbl_title.pack(anchor="w", padx=18, pady=(14, 6))
        lbl_val = tk.Label(card, text=initial_val, font=("Segoe UI", 32, "bold"), fg=self.colors["text_primary"], bg=self.colors["card_bg"])
        lbl_val.pack(anchor="w", padx=18, pady=(0, 6))
        lbl_sub = tk.Label(card, text=subtitle, font=("Segoe UI", 10), fg=self.colors["text_secondary"], bg=self.colors["card_bg"])
        lbl_sub.pack(anchor="w", padx=18, pady=(0, 14))
        card.val_label = lbl_val
        return card

    def save_auto_export_settings(self):
        if hasattr(self, 'auto_export_var') and hasattr(self, 'auto_day_combo'):
            self.auto_export_settings["enabled"] = self.auto_export_var.get()
            try:
                self.auto_export_settings["day"] = int(self.auto_day_combo.get())
            except ValueError:
                self.auto_export_settings["day"] = 1
            self.save_data()

    def check_auto_export_trigger(self):
        if not self.auto_export_settings.get("enabled", False):
            return
        
        today = datetime.date.today()
        target_day = self.auto_export_settings.get("day", 1)
        current_ym = today.strftime("%Y-%m")
        last_exported = self.auto_export_settings.get("last_exported_month", "")

        if today.day >= target_day and last_exported != current_ym:
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                backup_filename = f"finpulse_backup_{self.current_user}.csv"
                backup_path = os.path.join(script_dir, backup_filename)

                with open(backup_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Date", "Type", "Title/Payee", "Category", "Amount (INR)", "Frequency", "Method", "Status"])
                    for t in self.transactions:
                        writer.writerow([
                            t.get("date", ""),
                            t.get("type", "Expense"),
                            t.get("title", ""),
                            t.get("category", ""),
                            t.get("amount", 0.0),
                            t.get("frequency", ""),
                            t.get("source", ""),
                            t.get("status", "")
                        ])
                
                self.auto_export_settings["last_exported_month"] = current_ym
                self.save_data()
            except Exception as e:
                print(f"Auto-export error: {e}")

    def pick_export_date(self, entry_widget):
        dialog = CalendarDialog(self.root, initial_date=entry_widget.get().strip(), colors=self.colors)
        self.root.wait_window(dialog)
        if dialog.result_date:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, dialog.result_date)
            self.update_export_preview()

    def set_export_preset(self, preset_type):
        today = datetime.date.today()
        if preset_type == "all":
            self.exp_start_entry.delete(0, tk.END)
            self.exp_end_entry.delete(0, tk.END)
        elif preset_type == "this_month":
            first_day = today.replace(day=1).strftime("%Y-%m-%d")
            last_day_num = calendar.monthrange(today.year, today.month)[1]
            last_day = today.replace(day=last_day_num).strftime("%Y-%m-%d")
            self.exp_start_entry.delete(0, tk.END)
            self.exp_start_entry.insert(0, first_day)
            self.exp_end_entry.delete(0, tk.END)
            self.exp_end_entry.insert(0, last_day)
        elif preset_type == "30_days":
            s = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            e = today.strftime("%Y-%m-%d")
            self.exp_start_entry.delete(0, tk.END)
            self.exp_start_entry.insert(0, s)
            self.exp_end_entry.delete(0, tk.END)
            self.exp_end_entry.insert(0, e)
        elif preset_type == "90_days":
            s = (today - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
            e = today.strftime("%Y-%m-%d")
            self.exp_start_entry.delete(0, tk.END)
            self.exp_start_entry.insert(0, s)
            self.exp_end_entry.delete(0, tk.END)
            self.exp_end_entry.insert(0, e)
        self.update_export_preview()

    def get_export_filtered_dataset(self):
        s_date = self.exp_start_entry.get().strip()
        e_date = self.exp_end_entry.get().strip()
        t_type = self.exp_type_combo.get()

        res = self.transactions
        if s_date:
            res = [t for t in res if t.get("date", "") >= s_date]
        if e_date:
            res = [t for t in res if t.get("date", "") <= e_date]
        if t_type == "Expense Only":
            res = [t for t in res if t.get("type", "Expense") == "Expense"]
        elif t_type == "Income Only":
            res = [t for t in res if t.get("type", "Expense") == "Income"]
        return res

    def update_export_preview(self):
        if not hasattr(self, 'exp_tree'):
            return
        for row in self.exp_tree.get_children():
            self.exp_tree.delete(row)

        dataset = self.get_export_filtered_dataset()
        total_val = sum(t.get("amount", 0) for t in dataset)
        self.exp_summary_lbl.config(text=f"Records Found: {len(dataset)} | Total Value: ₹{total_val:,.2f}")

        for item in dataset:
            entry_type = item.get("type", "Expense")
            status = item.get("status", "Paid")
            self.exp_tree.insert("", "end", values=(
                item.get("date", "N/A"),
                entry_type,
                item.get("title", "N/A"),
                item.get("category", "Other"),
                f"₹{item.get('amount', 0):,.2f}",
                item.get("frequency", "Monthly"),
                item.get("source", "UPI Autopay"),
                status if entry_type == "Expense" else "Credited"
            ))

    def execute_export(self):
        dataset = self.get_export_filtered_dataset()
        if not dataset:
            messagebox.showwarning("No Data", "No transactions found matching the selected export date range and filters.")
            return

        fmt = self.exp_format_combo.get()
        if "CSV" in fmt:
            filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], title="Export Transactions as CSV")
            if filepath:
                try:
                    with open(filepath, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["Date", "Type", "Title/Payee", "Category", "Amount (INR)", "Frequency", "Method", "Status"])
                        for t in dataset:
                            writer.writerow([
                                t.get("date", ""),
                                t.get("type", "Expense"),
                                t.get("title", ""),
                                t.get("category", ""),
                                t.get("amount", 0.0),
                                t.get("frequency", ""),
                                t.get("source", ""),
                                t.get("status", "")
                            ])
                    messagebox.showinfo("Export Successful", f"Successfully exported {len(dataset)} records to:\n{filepath}")
                except Exception as e:
                    messagebox.showerror("Export Failed", f"Could not save CSV file: {e}")

        elif "JSON" in fmt:
            filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Export Transactions as JSON")
            if filepath:
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(dataset, f, indent=4)
                    messagebox.showinfo("Export Successful", f"Successfully exported {len(dataset)} records to:\n{filepath}")
                except Exception as e:
                    messagebox.showerror("Export Failed", f"Could not save JSON file: {e}")

        elif "PDF" in fmt:
            filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Documents", "*.pdf")], title="Export Transactions as PDF")
            if filepath:
                try:
                    fig = Figure(figsize=(8.5, 11), facecolor="white")
                    ax = fig.add_subplot(111)
                    ax.axis("off")

                    title_text = f"FinPulse Statement — User: {self.current_user.upper() if self.current_user else 'USER'}\nGenerated on: {datetime.date.today().strftime('%Y-%m-%d')}"
                    ax.text(0.05, 0.95, title_text, fontsize=12, fontweight="bold", verticalalignment="top")

                    headers = ["Date", "Type", "Title", "Category", "Amount (₹)", "Status"]
                    table_data = [headers]
                    for t in dataset:
                        table_data.append([
                            t.get("date", ""),
                            t.get("type", "Expense"),
                            t.get("title", "")[:18],
                            t.get("category", ""),
                            f"₹{t.get('amount', 0):,.2f}",
                            t.get("status", "")
                        ])

                    table = ax.table(cellText=table_data, loc="center", cellLoc="center")
                    table.auto_set_font_size(False)
                    table.set_fontsize(8)
                    table.scale(1, 1.2)

                    fig.savefig(filepath, format="pdf", bbox_inches="tight")
                    messagebox.showinfo("Export Successful", f"Successfully generated PDF statement:\n{filepath}")
                except Exception as e:
                    messagebox.showerror("Export Failed", f"Could not generate PDF: {e}")

    def create_metric_widget(self, parent, title, val_str, color):
        card = tk.Frame(parent, bg="#111827", highlightbackground="#374151", highlightthickness=1, padx=12, pady=10)
        tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg=self.colors["text_secondary"], bg="#111827").pack(anchor="w", pady=(2, 2))
        val_lbl = tk.Label(card, text=val_str, font=("Segoe UI", 16, "bold"), fg=color, bg="#111827")
        val_lbl.pack(anchor="w", pady=(0, 2))
        card.val_label = val_lbl
        return card

    def save_monthly_budget(self):
        curr_ym = datetime.date.today().strftime("%Y-%m")
        try:
            b_val = float(self.budget_entry.get().strip())
            if b_val < 0: raise ValueError
            self.budgets[curr_ym] = b_val
            self.save_data()
            messagebox.showinfo("Success", f"Monthly budget for {curr_ym} set to ₹{b_val:,.2f} successfully!")
            self.switch_page("Visual Analytics & Budget")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric budget amount.")

    def calculate_monthly_finances(self, ym):
        inc = sum(t.get("amount", 0) for t in self.transactions if t.get("type", "Expense") == "Income" and t.get("date", "").startswith(ym))
        exp = sum(t.get("amount", 0) for t in self.transactions if t.get("type", "Expense") == "Expense" and t.get("date", "").startswith(ym))
        return inc, exp, inc - exp

    def render_pie_chart(self, parent_frame, ym):
        fig = Figure(figsize=(5, 4), facecolor="#1E293B")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#0F172A")

        expenses = [t for t in self.transactions if t.get("type", "Expense") == "Expense" and t.get("date", "").startswith(ym)]
        
        cat_totals = {}
        for t in expenses:
            c = t.get("category", "Other")
            cat_totals[c] = cat_totals.get(c, 0) + t.get("amount", 0)

        cats = list(cat_totals.keys())
        amounts = list(cat_totals.values())

        color_palette = ["#38BDF8", "#22C55E", "#EAB308", "#A855F7", "#EF4444", "#F97316", "#EC4899", "#14B8A6", "#8B5CF6", "#64748B"]

        if cats and sum(amounts) > 0:
            wedges, texts, autotexts = ax.pie(
                amounts, 
                labels=cats, 
                autopct='%1.1f%%', 
                startangle=140, 
                colors=color_palette[:len(cats)],
                textprops=dict(color="#F8FAFC", fontsize=8)
            )
            for autotext in autotexts:
                autotext.set_color("#0F172A")
                autotext.set_weight("bold")

            def on_pie_click(event):
                if event.inaxes == ax:
                    for i, wedge in enumerate(wedges):
                        if wedge.contains_point([event.x, event.y]):
                            clicked_cat = cats[i]
                            self.active_categories = [clicked_cat]
                            
                            dt = datetime.datetime.strptime(ym + "-01", "%Y-%m-%d")
                            last_day = calendar.monthrange(dt.year, dt.month)[1]
                            self.filter_start_date = f"{ym}-01"
                            self.filter_end_date = f"{ym}-{last_day:02d}"

                            self.switch_page("All Transaction / filtering")
                            break

            canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            canvas.mpl_connect('button_press_event', on_pie_click)
        else:
            ax.text(0.5, 0.5, "No Expense Data for Current Month", color="#94A3B8", ha="center", va="center", transform=ax.transAxes)
            canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def render_line_graph(self, parent_frame):
        fig = Figure(figsize=(5, 4), facecolor="#1E293B")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#0F172A")

        monthly_expenses = {}
        for t in self.transactions:
            if t.get("type", "Expense") == "Expense":
                dt_str = t.get("date", "")
                if len(dt_str) >= 7:
                    ym = dt_str[:7]
                    monthly_expenses[ym] = monthly_expenses.get(ym, 0) + t.get("amount", 0)

        sorted_yms = sorted(monthly_expenses.keys())
        amounts = [monthly_expenses[ym] for ym in sorted_yms]

        if sorted_yms:
            ax.plot(sorted_yms, amounts, marker="o", color="#22C55E", linewidth=2.5, markersize=6)
            ax.set_ylabel("Total Expense (₹)", color="#F8FAFC", fontsize=9)
            ax.tick_params(colors="#94A3B8", labelsize=8)
            plt_plt = ax.get_xticklabels()
            for label in plt_plt:
                label.set_rotation(25)
                label.set_ha("right")
            ax.grid(True, color="#334155", linestyle="--", alpha=0.5)
        else:
            ax.text(0.5, 0.5, "No Historical Expense Data Found", color="#94A3B8", ha="center", va="center", transform=ax.transAxes)

        ax.spines["bottom"].set_color("#334155")
        ax.spines["top"].set_color("#334155")
        ax.spines["left"].set_color("#334155")
        ax.spines["right"].set_color("#334155")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def load_data(self):
        user_data_file = self.data_file.replace("finpulse_data.json", f"finpulse_data_{self.current_user}.json")
        if os.path.exists(user_data_file):
            try:
                with open(user_data_file, "r") as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        self.transactions = content
                        self.budgets = {}
                        self.auto_export_settings = {"enabled": False, "day": 1, "last_exported_month": ""}
                    else:
                        self.transactions = content.get("transactions", [])
                        self.budgets = content.get("budgets", {})
                        self.auto_export_settings = content.get("auto_export", {"enabled": False, "day": 1, "last_exported_month": ""})
                    for item in self.transactions:
                        if "type" not in item:
                            item["type"] = "Expense"
                        if "status" not in item:
                            item["status"] = "Pending" if item.get("category") in ["Bills & Utilities", "Utility"] else "Paid"
                        if "frequency" not in item:
                            item["frequency"] = "Monthly"
                        if "recurring" not in item:
                            item["recurring"] = item.get("frequency") != "One-Time"
                        if "selected" not in item:
                            item["selected"] = False
            except Exception:
                self.transactions = []
                self.budgets = {}
                self.auto_export_settings = {"enabled": False, "day": 1, "last_exported_month": ""}
        else:
            self.transactions = []
            self.budgets = {}
            self.auto_export_settings = {"enabled": False, "day": 1, "last_exported_month": ""}

    def save_data(self):
        user_data_file = self.data_file.replace("finpulse_data.json", f"finpulse_data_{self.current_user}.json")
        try:
            data_to_save = {
                "transactions": self.transactions,
                "budgets": self.budgets,
                "auto_export": self.auto_export_settings
            }
            with open(user_data_file, "w") as f:
                json.dump(data_to_save, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

    def parse_upi_sms(self):
        sms_text = self.upi_sms_entry.get().strip()
        if not sms_text:
            messagebox.showwarning("Empty Payload", "Please enter a simulated SMS string.")
            return
        amount_match = re.search(r'(?:INR|Rs\.?|₹)\s*([\d,]+\.?\d*)', sms_text, re.IGNORECASE)
        to_match = re.search(r'(?:to|from)\s+([A-Za-z0-9\s]+?)\s+(?:via|Ref|on|Utility|\d)', sms_text, re.IGNORECASE)
        is_credit = "credit" in sms_text.lower() or "salary" in sms_text.lower()
        is_debit = "debit" in sms_text.lower() and "bill generated" not in sms_text.lower()
        
        entry_type = "Income" if is_credit else "Expense"
        
        if amount_match:
            amount = float(amount_match.group(1).replace(',', ''))
            merchant = to_match.group(1).strip() if to_match else ("Salary Source" if is_credit else "UPI Merchant")
            category = "Salary" if is_credit else "Subscription"
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
            elif any(k in merchant_upper for k in ["SALARY", "CREDIT", "PAY"]):
                category = "Salary"
            
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
            
            status = "Pending" if (entry_type == "Expense" and category == "Utility" and not is_debit) else ("Paid" if (is_debit or is_credit) else "Pending")
            today_date = datetime.date.today().strftime("%Y-%m-%d")
            new_txn = {
                "type": entry_type,
                "date": today_date,
                "title": merchant,
                "category": category,
                "amount": amount,
                "frequency": "Monthly",
                "source": "Direct Credit" if is_credit else "UPI Autopay",
                "status": status,
                "recurring": True,
                "selected": False
            }
            self.transactions.insert(0, new_txn)
            self.save_data()
            self.refresh_ui()
            msg = f"Intercepted Entry:\n• Type: {entry_type}\n• Payee/Source: {merchant}\n• Amount: ₹{amount:,.2f}\n• Status: {status}"
            if auto_updated_pending:
                msg += "\n\n⚡ Automatically updated matching 'Pending' bill to 'Paid'!"
            messagebox.showinfo("⚡ Auto-Captured!", msg)
        else:
            messagebox.showerror("Parsing Error", "Could not parse amount from SMS. Ensure format contains 'INR <amount>'.")

    def add_transaction(self):
        entry_type = self.type_combobox.get()
        date_str = self.date_entry.get().strip()
        title = self.title_entry.get().strip()
        category = self.category_combobox.get()
        amount_str = self.amount_entry.get().strip()
        frequency = self.frequency_combobox.get()
        if not title:
            messagebox.showerror("Error", "Please enter a payee or source title.")
            return
        try:
            amount = float(amount_str)
            if amount <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount.")
            return
        status = "Pending" if (entry_type == "Expense" and category in ["Utility", "Bills & Utilities"]) else "Paid"
        is_recurring = frequency != "One-Time"
        new_txn = {
            "type": entry_type,
            "date": date_str,
            "title": title,
            "category": category,
            "amount": amount,
            "frequency": frequency,
            "source": "Direct Credit" if entry_type == "Income" else "UPI Autopay",
            "status": status,
            "recurring": is_recurring,
            "selected": False
        }
        self.transactions.insert(0, new_txn)
        self.save_data()
        self.reset_entry_form()
        self.refresh_ui()
        messagebox.showinfo("Success", "Financial entry added successfully!")

    def edit_transaction_by_index(self, idx):
        if 0 <= idx < len(self.transactions):
            item = self.transactions[idx]
            dialog = EditTransactionDialog(self.root, item, colors=self.colors)
            self.root.wait_window(dialog)
            if dialog.updated_data:
                self.transactions[idx] = dialog.updated_data
                self.save_data()
                self.refresh_ui()
                messagebox.showinfo("Success", "Financial entry updated successfully!")

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
            messagebox.showwarning("Warning", "Select a financial entry checkbox or row to edit.")
            return
        self.edit_transaction_by_index(selected_indices[0])

    def reset_entry_form(self):
        self.title_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.type_combobox.set("Expense")
        self.category_combobox.set("Utility")
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
                    if col == "#8":
                        current_status = actual_txn.get("status", "Paid")
                        actual_txn["status"] = "Pending" if current_status == "Paid" else "Paid"
                        self.save_data()
                        self.refresh_ui()
                    elif col == "#9":
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
            messagebox.showwarning("Warning", "Select financial entry checkboxes to delete.")
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected_indices)} transaction(s)?"):
            self.transactions = [t for i, t in enumerate(self.transactions) if i not in selected_indices]
            self.save_data()
            self.refresh_ui()

    def get_filtered_transactions(self):
        filtered = self.transactions
        if self.active_categories:
            filtered = [t for t in filtered if t.get("category") in self.active_categories]
        if self.filter_start_date:
            filtered = [t for t in filtered if t.get("date", "") >= self.filter_start_date]
        if self.filter_end_date:
            filtered = [t for t in filtered if t.get("date", "") <= self.filter_end_date]
        return filtered

    def open_filter_dialog(self):
        dialog = MultiFilterDialog(self.root, self.available_categories, self.active_categories, start_date=self.filter_start_date, end_date=self.filter_end_date, colors=self.colors)
        self.root.wait_window(dialog)
        self.active_categories = dialog.selected_categories
        self.filter_start_date = dialog.start_date
        self.filter_end_date = dialog.end_date
        self.refresh_ui()

    def clear_filters(self):
        self.active_categories = []
        self.filter_start_date = ""
        self.filter_end_date = ""
        self.refresh_ui()

    def load_sample_sms(self, event):
        sel = self.sample_combobox.get()
        if sel != "Select sample notification...":
            self.upi_sms_entry.delete(0, tk.END)
            self.upi_sms_entry.insert(0, sel)

    def open_calendar_picker(self):
        curr_val = self.date_entry.get().strip()
        dialog = CalendarDialog(self.root, initial_date=curr_val, colors=self.colors)
        self.root.wait_window(dialog)
        if dialog.result_date:
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, dialog.result_date)

    def update_health_banner(self):
        if self.active_page != "Home":
            return
        pending_bills = [t for t in self.transactions if t.get("type", "Expense") == "Expense" and t.get("status") == "Pending"]
        subscriptions = [t for t in self.transactions if t.get("category") == "Subscription"]
        
        today = datetime.date.today()
        curr_ym = today.strftime("%Y-%m")
        first_day_curr = today.replace(day=1)
        prev_ym = (first_day_curr - datetime.timedelta(days=1)).strftime("%Y-%m")
        
        curr_month_exp = sum(t.get("amount", 0) for t in self.transactions if t.get("type", "Expense") == "Expense" and t.get("date", "").startswith(curr_ym))
        prev_month_exp = sum(t.get("amount", 0) for t in self.transactions if t.get("type", "Expense") == "Expense" and t.get("date", "").startswith(prev_ym))
        
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
                text="👁️ Watch Analytics", bg="#7E22CE", fg="white", activebackground="#6B21A8",
                command=lambda: self.switch_page("Visual Analytics & Budget")
            )
            self.banner_action_btn.pack(side="right")

        elif alert_type == "redundant_subs":
            self.banner_card.config(bg="#9A3412", highlightbackground="#EA580C")
            banner_top.config(bg="#9A3412")
            self.banner_title.config(text="🟠 Redundant Subscription Warning", bg="#9A3412", fg="#FFEDD5")
            self.banner_desc.config(text="You have multiple active subscriptions in similar service categories. Review active subscriptions below!", bg="#9A3412", fg="#FED7AA")
            self.banner_action_btn.config(
                text="🔍 Review Subscriptions", bg="#EA580C", fg="white", activebackground="#C2410C",
                command=lambda: (self.switch_page("All Transaction / filtering"), setattr(self, 'active_categories', ['Subscription']), self.refresh_ui())
            )
            self.banner_action_btn.pack(side="right")

        elif alert_type == "success":
            total_committed = sum(
                t.get("amount", 0) if t.get("frequency", "Monthly") == "Monthly"
                else t.get("amount", 0) / 12 if t.get("frequency") == "Annually"
                else 0 for t in self.transactions if t.get("type", "Expense") == "Expense"
            )
            self.banner_card.config(bg="#064E3B", highlightbackground="#059669")
            banner_top.config(bg="#064E3B")
            self.banner_title.config(text="✅ Financial Health: Looking Great!", bg="#064E3B", fg="#34D399")
            self.banner_desc.config(text=f"You are doing well! Committed Monthly Spend: ₹{total_committed:,.2f} | Active Scheduled Payments: {len(self.transactions)} | Pending Bills: None.", bg="#064E3B", fg="#A7F3D0")
            self.banner_action_btn.pack_forget()

    def refresh_ui(self):
        total_committed = sum(
            item.get("amount", 0) if item.get("frequency", "Monthly") == "Monthly"
            else item.get("amount", 0) / 12 if item.get("frequency") == "Annually"
            else 0
            for item in self.transactions if item.get("type", "Expense") == "Expense"
        )
        emis_total = sum(
            item.get("amount", 0) if item.get("frequency", "Monthly") == "Monthly"
            else item.get("amount", 0) / 12 if item.get("frequency") == "Annually"
            else 0
            for item in self.transactions if item.get("type", "Expense") == "Expense" and item.get("category") == "EMI"
        )
        pending_count = sum(1 for item in self.transactions if item.get("type", "Expense") == "Expense" and item.get("status") == "Pending")
        total_payments = len(self.transactions)
        
        if self.active_page == "Home":
            self.card_committed.val_label.config(text=f"₹{total_committed:,.0f}")
            self.card_emis.val_label.config(text=f"₹{emis_total:,.0f}")
            self.card_due.val_label.config(text=f"{pending_count} Bills")
            self.card_mandates.val_label.config(text=f"{total_payments} Total")
            self.update_health_banner()
        elif self.active_page == "Visual Analytics & Budget":
            pass
        elif self.active_page == "Export Data":
            self.update_export_preview()
        elif self.active_page == "All Transaction / filtering":
            if hasattr(self, 'active_filters_lbl'):
                filter_texts = []
                if self.active_categories:
                    filter_texts.append(f"Categories: {', '.join(self.active_categories)}")
                if self.filter_start_date or self.filter_end_date:
                    s = self.filter_start_date if self.filter_start_date else "Start"
                    e = self.filter_end_date if self.filter_end_date else "End"
                    filter_texts.append(f"Date: {s} to {e}")

                if filter_texts:
                    self.active_filters_lbl.config(text=" | ".join(filter_texts))
                    self.clear_filter_btn.pack(side="left", padx=(0, 10))
                else:
                    self.active_filters_lbl.config(text="Showing All Transactions")
                    self.clear_filter_btn.pack_forget()

            for row in self.tree.get_children():
                self.tree.delete(row)
            filtered = self.get_filtered_transactions()
            for item in filtered:
                entry_type = item.get("type", "Expense")
                status = item.get("status", "Paid")
                tag_name = "income" if entry_type == "Income" else ("pending" if status == "Pending" else "paid")
                freq = item.get("frequency", "Monthly")
                freq_icon = f"🔁 {freq}" if freq != "One-Time" else "One-Time"
                chk_icon = "[ ✓ ]" if item.get("selected", False) else "[   ]"
                self.tree.insert("", "end", values=(
                    item.get("date", "N/A"),
                    entry_type,
                    item.get("title", "N/A"),
                    item.get("category", "Other"),
                    f"₹{item.get('amount', 0):,.2f}",
                    freq_icon,
                    item.get("source", "UPI Autopay"),
                    status if entry_type == "Expense" else "Credited",
                    chk_icon
                ), tags=(tag_name,))

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernFinPulseApp(root)
    root.mainloop()