import json
import os
import re
import datetime
import tkinter as tk
from tkinter import messagebox, ttk

class ModernFinPulseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FinPulse Desktop — Modern Automated Expense Tracker")
        self.root.geometry("1120x720")
        self.root.minsize(1020, 650)
        self.root.configure(bg="#0F172A")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(script_dir, "finpulse_data.json")
        self.transactions = self.load_data()

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
                        rowheight=32,
                        font=("Segoe UI", 10),
                        borderwidth=0)
        style.map("Treeview", background=[("selected", "#38BDF8")], foreground=[("selected", "#0F172A")])
        style.configure("Treeview.Heading",
                        background="#334155",
                        foreground="#F8FAFC",
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0)

    def build_layout(self):
        top_bar = tk.Frame(self.root, bg=self.colors["sidebar_bg"], height=60, highlightbackground=self.colors["card_border"], highlightthickness=1)
        top_bar.pack(fill="x", side="top")

        brand_frame = tk.Frame(top_bar, bg=self.colors["sidebar_bg"])
        brand_frame.pack(side="left", padx=20, pady=10)

        brand_logo = tk.Label(brand_frame, text="⚡", font=("Segoe UI", 18, "bold"), fg=self.colors["accent_blue"], bg=self.colors["sidebar_bg"])
        brand_logo.pack(side="left")

        brand_title = tk.Label(brand_frame, text="FinPulse", font=("Segoe UI", 16, "bold"), fg=self.colors["text_primary"], bg=self.colors["sidebar_bg"])
        brand_title.pack(side="left", padx=(5, 10))

        badge = tk.Label(brand_frame, text="PRO DESKTOP", font=("Segoe UI", 8, "bold"), fg=self.colors["accent_purple"], bg="#3B0764", padx=8, pady=2)
        badge.pack(side="left")

        status_lbl = tk.Label(top_bar, text="🟢 Real-Time UPI Sync Active", font=("Segoe UI", 9, "bold"), fg=self.colors["accent_green"], bg=self.colors["sidebar_bg"])
        status_lbl.pack(side="right", padx=20)

        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        left_panel = tk.Frame(main_container, bg=self.colors["bg"], width=380)
        left_panel.pack(side="left", fill="y", padx=(0, 15))

        right_panel = tk.Frame(main_container, bg=self.colors["bg"])
        right_panel.pack(side="right", fill="both", expand=True)

        upi_card = tk.LabelFrame(left_panel, text=" ⚡ Instant UPI / SMS Interceptor ", font=("Segoe UI", 11, "bold"),
                                 bg=self.colors["card_bg"], fg=self.colors["accent_blue"],
                                 bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        upi_card.pack(fill="x", pady=(0, 15), ipadx=10, ipady=10)

        upi_desc = tk.Label(upi_card, text="Simulate real-time push notification / SMS from Google Pay, PhonePe, or Bank:",
                            font=("Segoe UI", 8), fg=self.colors["text_secondary"], bg=self.colors["card_bg"], wraplength=340, justify="left")
        upi_desc.pack(anchor="w", padx=10, pady=(5, 8))

        self.upi_sms_entry = tk.Entry(upi_card, font=("Segoe UI", 9), bg=self.colors["input_bg"], fg=self.colors["text_primary"],
                                      insertbackground="white", bd=1, relief="solid")
        self.upi_sms_entry.pack(fill="x", padx=10, pady=5, ipady=6)
        self.upi_sms_entry.insert(0, "A/c XX1234 debited by INR 350.00 on 2026-10-22 to SWIGGY via UPI Ref 928301")

        parse_btn = tk.Button(upi_card, text="⚡ Auto-Capture Transaction", font=("Segoe UI", 10, "bold"),
                              bg=self.colors["accent_blue"], fg="#0F172A", activebackground="#0284C7",
                              bd=0, cursor="hand2", command=self.parse_upi_sms)
        parse_btn.pack(fill="x", padx=10, pady=(8, 5), ipady=6)

        manual_card = tk.LabelFrame(left_panel, text=" 📝 Manual Record Entry ", font=("Segoe UI", 11, "bold"),
                                    bg=self.colors["card_bg"], fg=self.colors["text_primary"],
                                    bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        manual_card.pack(fill="x", ipadx=10, ipady=10)

        tk.Label(manual_card, text="Date (YYYY-MM-DD):", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=10, pady=(5, 0))
        self.date_entry = tk.Entry(manual_card, font=("Segoe UI", 9), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.date_entry.pack(fill="x", padx=10, pady=3, ipady=4)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        tk.Label(manual_card, text="Merchant / Title:", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=10, pady=(5, 0))
        self.title_entry = tk.Entry(manual_card, font=("Segoe UI", 9), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.title_entry.pack(fill="x", padx=10, pady=3, ipady=4)

        tk.Label(manual_card, text="Category:", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=10, pady=(5, 0))
        self.category_combobox = ttk.Combobox(manual_card, values=["Food & Dining", "Groceries", "Subscriptions", "Bills & Utilities", "Shopping", "Transport", "Other"], font=("Segoe UI", 9), state="readonly")
        self.category_combobox.pack(fill="x", padx=10, pady=3, ipady=2)
        self.category_combobox.set("Food & Dining")

        tk.Label(manual_card, text="Amount (₹):", font=("Segoe UI", 9), fg=self.colors["text_secondary"], bg=self.colors["card_bg"]).pack(anchor="w", padx=10, pady=(5, 0))
        self.amount_entry = tk.Entry(manual_card, font=("Segoe UI", 9), bg=self.colors["input_bg"], fg=self.colors["text_primary"], insertbackground="white")
        self.amount_entry.pack(fill="x", padx=10, pady=3, ipady=4)

        save_btn = tk.Button(manual_card, text="+ Add Entry", font=("Segoe UI", 10, "bold"),
                             bg=self.colors["button_green"], fg="white", activebackground=self.colors["button_green_hover"],
                             bd=0, cursor="hand2", command=self.add_manual_transaction)
        save_btn.pack(fill="x", padx=10, pady=(12, 5), ipady=6)

        stats_frame = tk.Frame(right_panel, bg=self.colors["bg"])
        stats_frame.pack(fill="x", pady=(0, 15))

        self.card_total = self.create_stat_card(stats_frame, "TOTAL SPEND", "₹0.00", self.colors["accent_blue"])
        self.card_total.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.card_month = self.create_stat_card(stats_frame, "THIS MONTH", "₹0.00", self.colors["accent_green"])
        self.card_month.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.card_subs = self.create_stat_card(stats_frame, "PENDING BILLS", "0 Bills", self.colors["accent_yellow"])
        self.card_subs.pack(side="left", fill="x", expand=True)

        chart_card = tk.LabelFrame(right_panel, text=" 📊 Category Spend Analytics ", font=("Segoe UI", 11, "bold"),
                                   bg=self.colors["card_bg"], fg=self.colors["text_primary"],
                                   bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        chart_card.pack(fill="x", pady=(0, 15))

        self.chart_canvas = tk.Canvas(chart_card, bg=self.colors["card_bg"], height=120, highlightthickness=0)
        self.chart_canvas.pack(fill="x", padx=10, pady=10)

        table_card = tk.LabelFrame(right_panel, text=" 📜 Transaction Ledger (Click 'Paid'/'Pending' in table to toggle) ", font=("Segoe UI", 11, "bold"),
                                    bg=self.colors["card_bg"], fg=self.colors["text_primary"],
                                    bd=1, relief="solid", highlightbackground=self.colors["card_border"])
        table_card.pack(fill="both", expand=True)

        scroll = ttk.Scrollbar(table_card)
        scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(table_card, columns=("date", "title", "category", "amount", "source", "status"), show="headings", yscrollcommand=scroll.set)
        scroll.config(command=self.tree.yview)

        self.tree.heading("date", text="Date")
        self.tree.heading("title", text="Merchant / Description")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount (₹)")
        self.tree.heading("source", text="Source")
        self.tree.heading("status", text="Status")

        self.tree.column("date", width=95, anchor="center")
        self.tree.column("title", width=180, anchor="w")
        self.tree.column("category", width=110, anchor="center")
        self.tree.column("amount", width=95, anchor="e")
        self.tree.column("source", width=95, anchor="center")
        self.tree.column("status", width=95, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.tag_configure("pending", foreground="#EF4444")
        self.tree.tag_configure("paid", foreground="#22C55E")

        self.tree.bind("<Button-1>", self.handle_tree_click)

        table_actions = tk.Frame(table_card, bg=self.colors["card_bg"])
        table_actions.pack(fill="x", padx=10, pady=(0, 10))

        del_btn = tk.Button(table_actions, text="Delete Selected", font=("Segoe UI", 9, "bold"),
                            bg=self.colors["accent_red"], fg="white", bd=0, cursor="hand2", command=self.delete_transaction)
        del_btn.pack(side="right")

    def create_stat_card(self, parent, title, initial_val, accent_color):
        card = tk.Frame(parent, bg=self.colors["card_bg"], highlightbackground=self.colors["card_border"], highlightthickness=1)
        lbl_title = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg=self.colors["text_secondary"], bg=self.colors["card_bg"])
        lbl_title.pack(anchor="w", padx=15, pady=(10, 2))
        lbl_val = tk.Label(card, text=initial_val, font=("Segoe UI", 16, "bold"), fg=accent_color, bg=self.colors["card_bg"])
        lbl_val.pack(anchor="w", padx=15, pady=(0, 10))
        card.val_label = lbl_val
        return card

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    for item in data:
                        if "status" not in item:
                            item["status"] = "Pending" if item.get("category") == "Bills & Utilities" else "Paid"
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
        to_match = re.search(r'to\s+([A-Za-z0-9\s]+?)\s+(?:via|Ref|on|\d)', sms_text, re.IGNORECASE)

        if amount_match:
            amount = float(amount_match.group(1).replace(',', ''))
            merchant = to_match.group(1).strip() if to_match else "UPI Merchant"
            
            category = "Other"
            merchant_upper = merchant.upper()
            if any(k in merchant_upper for k in ["SWIGGY", "ZOMATO", "CAFE", "RESTO"]):
                category = "Food & Dining"
            elif any(k in merchant_upper for k in ["BLINKIT", "ZEPTO", "GROCERY", "MART"]):
                category = "Groceries"
            elif any(k in merchant_upper for k in ["NETFLIX", "SPOTIFY", "PRIME"]):
                category = "Subscriptions"
            elif any(k in merchant_upper for k in ["BESCOM", "ELECTRICITY", "WATER", "AIRTEL", "JIO", "BILL"]):
                category = "Bills & Utilities"
            elif any(k in merchant_upper for k in ["UBER", "OLA", "PETROL"]):
                category = "Transport"

            status = "Pending" if category == "Bills & Utilities" else "Paid"
            today_date = datetime.date.today().strftime("%Y-%m-%d")

            new_txn = {
                "date": today_date,
                "title": merchant,
                "category": category,
                "amount": amount,
                "source": "UPI Auto-Sync",
                "status": status
            }

            self.transactions.insert(0, new_txn)
            self.save_data()
            self.refresh_ui()

            messagebox.showinfo("⚡ Auto-Captured!", f"Intercepted UPI payment:\n• Merchant: {merchant}\n• Amount: ₹{amount:,.2f}\n• Status: {status}")
        else:
            messagebox.showerror("Parsing Error", "Could not parse amount from SMS. Ensure format contains 'INR <amount>'.")

    def add_manual_transaction(self):
        date_str = self.date_entry.get().strip()
        title = self.title_entry.get().strip()
        category = self.category_combobox.get()
        amount_str = self.amount_entry.get().strip()

        if not title:
            messagebox.showerror("Error", "Please enter a merchant title.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount.")
            return

        status = "Pending" if category == "Bills & Utilities" else "Paid"

        new_txn = {
            "date": date_str,
            "title": title,
            "category": category,
            "amount": amount,
            "source": "Manual Entry",
            "status": status
        }

        self.transactions.insert(0, new_txn)
        self.save_data()
        
        self.title_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.refresh_ui()

    def handle_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            col = self.tree.identify_column(event.x)
            if col == "#6":
                row_id = self.tree.identify_row(event.y)
                if row_id:
                    idx = self.tree.index(row_id)
                    if 0 <= idx < len(self.transactions):
                        current_status = self.transactions[idx].get("status", "Paid")
                        new_status = "Pending" if current_status == "Paid" else "Paid"
                        self.transactions[idx]["status"] = new_status
                        self.save_data()
                        self.refresh_ui()

    def delete_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select a transaction from the table to delete.")
            return

        idx = self.tree.index(selected_item[0])
        if 0 <= idx < len(self.transactions):
            removed = self.transactions.pop(idx)
            self.save_data()
            self.refresh_ui()

    def refresh_ui(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for item in self.transactions:
            status = item.get("status", "Paid")
            tag_name = "pending" if status == "Pending" else "paid"
    
            self.tree.insert("", "end", values=(
                item.get("date", "N/A"),
                item.get("title", "N/A"),
                item.get("category", "Other"),
                f"₹{item.get('amount', 0):,.2f}",
                item.get("source", "Manual"),
                status
            ), tags=(tag_name,))

        total_spend = sum(item.get("amount", 0) for item in self.transactions)
        current_month_prefix = datetime.date.today().strftime("%Y-%m")
        month_spend = sum(item.get("amount", 0) for item in self.transactions if item.get("date", "").startswith(current_month_prefix))
        pending_count = sum(1 for item in self.transactions if item.get("status") == "Pending")

        self.card_total.val_label.config(text=f"₹{total_spend:,.2f}")
        self.card_month.val_label.config(text=f"₹{month_spend:,.2f}")
        self.card_subs.val_label.config(text=f"{pending_count} Bills")

        self.draw_chart()

    def draw_chart(self):
        self.chart_canvas.delete("all")
        if not self.transactions:
            self.chart_canvas.create_text(250, 60, text="No transactions recorded yet.", fill=self.colors["text_secondary"], font=("Segoe UI", 10))
            return

        cat_totals = {}
        for item in self.transactions:
            cat = item.get("category", "Other")
            cat_totals[cat] = cat_totals.get(cat, 0) + item.get("amount", 0)

        categories = list(cat_totals.keys())[:5]
        max_val = max(cat_totals.values()) if cat_totals else 1

        canvas_width = self.chart_canvas.winfo_width()
        if canvas_width < 100: canvas_width = 600

        bar_height = 14
        start_y = 10

        for i, cat in enumerate(categories):
            val = cat_totals[cat]
            ratio = val / max_val
            bar_w = max(int(ratio * (canvas_width - 220)), 10)
            y = start_y + (i * 22)
            
            self.chart_canvas.create_text(10, y + 7, text=cat, anchor="w", fill=self.colors["text_secondary"], font=("Segoe UI", 8, "bold"))
            self.chart_canvas.create_rectangle(110, y, canvas_width - 100, y + bar_height, fill="#0F172A", outline="")
            self.chart_canvas.create_rectangle(110, y, 110 + bar_w, y + bar_height, fill=self.colors["accent_blue"], outline="")
            self.chart_canvas.create_text(120 + bar_w, y + 7, text=f"₹{val:,.0f}", anchor="w", fill=self.colors["text_primary"], font=("Segoe UI", 8))

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernFinPulseApp(root)
    root.mainloop()