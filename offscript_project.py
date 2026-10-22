<<<<<<< HEAD
import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

class DesktopFinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FinPulse Desktop - Expense & Bill Tracker")
        self.root.geometry("480x680")
        self.root.config(bg="#f0f2f5")

        # --- FIX: Force data file to live in the exact same folder as app.py ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(script_dir, "finpulse_data.json")
        
        self.transactions = self.load_data()

        # --- Header Title ---
        title_label = tk.Label(root, text="💳 FinPulse Desktop Tracker", font=("Arial", 16, "bold"), bg="#f0f2f5", fg="#333")
        title_label.pack(pady=10)

        subtitle_label = tk.Label(root, text="Consolidate UPI, cards, subscriptions & bills", font=("Arial", 10), bg="#f0f2f5", fg="#666")
        subtitle_label.pack(pady=2)

        # --- Input Form Frame ---
        form_frame = tk.LabelFrame(root, text=" Add New Payment ", font=("Arial", 11, "bold"), bg="#f0f2f5", padx=15, pady=10)
        form_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(form_frame, text="Transaction Title / Merchant:", bg="#f0f2f5", anchor="w").pack(fill="x")
        self.title_entry = tk.Entry(form_frame, font=("Arial", 11))
        self.title_entry.pack(fill="x", pady=3)

        tk.Label(form_frame, text="Category:", bg="#f0f2f5", anchor="w").pack(fill="x")
        self.category_combobox = ttk.Combobox(form_frame, values=["Subscriptions", "Bills & Utilities", "EMIs", "UPI / Cards", "Groceries", "Other"], font=("Arial", 11), state="readonly")
        self.category_combobox.pack(fill="x", pady=3)
        self.category_combobox.set("Subscriptions")

        tk.Label(form_frame, text="Amount (₹):", bg="#f0f2f5", anchor="w").pack(fill="x")
        self.amount_entry = tk.Entry(form_frame, font=("Arial", 11))
        self.amount_entry.pack(fill="x", pady=3)

        save_btn = tk.Button(form_frame, text="Record Transaction", font=("Arial", 11, "bold"), bg="#238636", fg="white", activebackground="#2ea043", command=self.add_transaction)
        save_btn.pack(fill="x", pady=8)

        # --- Summary Section ---
        self.summary_label = tk.Label(root, text="", font=("Arial", 10, "bold"), bg="#e1dfdd", fg="#111", padx=10, pady=6)
        self.summary_label.pack(fill="x", padx=20, pady=5)
        self.update_summary()

        # --- Ledger List Box & Controls ---
        tk.Label(root, text="Transaction Ledger:", font=("Arial", 11, "bold"), bg="#f0f2f5", anchor="w").pack(fill="x", padx=20)
        
        self.ledger_listbox = tk.Listbox(root, font=("Courier", 10), height=7)
        self.ledger_listbox.pack(fill="both", padx=20, pady=3, expand=True)
        self.refresh_ledger()

        delete_btn = tk.Button(root, text="Delete Selected Transaction", font=("Arial", 10), bg="#da3633", fg="white", activebackground="#b62324", command=self.delete_transaction)
        delete_btn.pack(fill="x", padx=20, pady=5)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_data(self):
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.transactions, f, indent=4)
        except Exception as e:
            messagebox.showerror("Storage Error", f"Could not save data: {e}")

    def add_transaction(self):
        title = self.title_entry.get().strip()
        category = self.category_combobox.get()
        amount_str = self.amount_entry.get().strip()

        if not title:
            messagebox.showerror("Error", "Please enter a transaction title.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount.")
            return

        self.transactions.append({"title": title, "category": category, "amount": amount})
        self.save_data()
        
        self.title_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

        self.refresh_ledger()
        self.update_summary()
        messagebox.showinfo("Success", "Transaction recorded successfully!")

    def delete_transaction(self):
        selected_indices = self.ledger_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Warning", "Please select a transaction from the ledger to delete.")
            return

        index = selected_indices[0]
        if 0 <= index < len(self.transactions):
            removed = self.transactions.pop(index)
            self.save_data()
            self.refresh_ledger()
            self.update_summary()
            messagebox.showinfo("Deleted", f"Removed: {removed['title']}")

    def refresh_ledger(self):
        self.ledger_listbox.delete(0, tk.END)
        if not self.transactions:
            self.ledger_listbox.insert(tk.END, "No transactions recorded yet.")
        else:
            for item in self.transactions:
                row_text = f"{item['title']:<18} | {item['category']:<15} | ₹{item['amount']:,.2f}"
                self.ledger_listbox.insert(tk.END, row_text)

    def update_summary(self):
        total = sum(item["amount"] for item in self.transactions)
        sub_total = sum(item["amount"] for item in self.transactions if item["category"] == "Subscriptions")
        self.summary_label.config(text=f"Total Expenses: ₹{total:,.2f}  |  Subscriptions: ₹{sub_total:,.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DesktopFinanceApp(root)
    root.mainloop()
=======

>>>>>>> cef557bd0cd6ca3c2298da41ad0e8b0a700644e5
