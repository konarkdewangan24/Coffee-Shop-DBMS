import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from typing import List
from cafe import CafeBillingSystem, OrderItem, Order, MenuItem # Import necessary classes from cafe.py

class CafeBillingGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Cafe Billing System")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f5f7fa")
        self.root.minsize(900, 650)

        # Initialize billing system logic (now connected to MySQL)
        try:
            self.system = CafeBillingSystem()
        except ConnectionError as e:
            messagebox.showerror("Database Connection Error", str(e))
            self.root.quit() # Use quit to properly close the window
            return

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use clam for better styling
        self.style.configure("TFrame", background="#f5f7fa")
        self.style.configure("Card.TFrame", background="#ffffff", relief="raised", borderwidth=1)
        self.style.configure("Header.TLabel", font=("Poppins", 26, "bold"), foreground="#1e293b", background="#f5f7fa")
        self.style.configure("Section.TLabel", font=("Poppins", 18, "bold"), foreground="#334155", background="#ffffff")
        self.style.configure("TLabel", font=("Poppins", 13), foreground="#475569", background="#f5f7fa")
        self.style.configure("Bold.TLabel", font=("Poppins", 13, "bold"), foreground="#334155", background="#f5f7fa")
        self.style.configure("TButton",
                             font=("Poppins", 13, "bold"),
                             foreground="#ffffff",
                             background="#2563eb",
                             padding=8)
        self.style.map("TButton",
            foreground=[('pressed', '#ffffff'), ('active', '#e0e7ff')],
            background=[('pressed', '#1e40af'), ('active', '#3b82f6')]
        )
        self.style.configure("Danger.TButton",
                             font=("Poppins", 11, "bold"),
                             foreground="#ffffff",
                             background="#dc2626",
                             padding=5)
        self.style.map("Danger.TButton",
            foreground=[('pressed', '#ffffff'), ('active', '#fee2e2')],
            background=[('pressed', '#b91c1c'), ('active', '#ef4444')]
        )
        self.style.configure("Treeview.Heading", font=("Poppins", 12, "bold"), foreground="#1e293b")
        self.style.configure("Treeview", font=("Poppins", 12), rowheight=26)

        # Fonts
        self.header_font = Font(family="Poppins", size=26, weight="bold")
        self.section_font = Font(family="Poppins", size=18, weight="bold")
        self.normal_font = Font(family="Poppins", size=13)

        # Create UI components
        self.create_header()
        self.create_navbar()
        self.create_main_area()

        # Internal state for place order
        self.current_order_items: List[OrderItem] = []

        # Show default view
        self.show_new_order_view()

    def create_header(self):
        header_frame = ttk.Frame(self.root, style="TFrame")
        header_frame.pack(fill="x", pady=(15,10), padx=30)
        header_label = ttk.Label(header_frame, text="Chaicoffee Cafe Billing System", style="Header.TLabel")
        header_label.pack(side="left", anchor="w")

    def create_navbar(self):
        nav_frame = ttk.Frame(self.root, style="TFrame")
        nav_frame.pack(fill="x", padx=30, pady=(0,20))

        buttons = [
            ("Place New Order", self.show_new_order_view),
            ("View Order", self.show_view_order_view),
            ("Daily Sales Report", self.show_daily_sales_report_view),
            ("Customer History", self.show_customer_history_view),
            ("Exit", self.root.quit),
        ]

        for (text, cmd) in buttons:
            btn = ttk.Button(nav_frame, text=text, command=cmd)
            btn.pack(side="left", padx=12, pady=5)

    def create_main_area(self):
        self.main_frame = ttk.Frame(self.root, style="TFrame")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=10)

    def clear_main_area(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    ##############################################################################
    # ------------------------ PLACE NEW ORDER VIEW -----------------------------
    ##############################################################################
    def show_new_order_view(self):
        self.clear_main_area()
        self.current_order_items.clear()

        title = ttk.Label(self.main_frame, text="Place New Order", style="Section.TLabel")
        title.pack(anchor="w", pady=(0,20))

        container = ttk.Frame(self.main_frame, style="TFrame")
        container.pack(fill="both", expand=True)

        # Left side frame: Customer info & add item
        left_frame = ttk.Frame(container, style="Card.TFrame", padding=20)
        left_frame.pack(side="left", fill="y", expand=False)

        # Customer Info
        cust_frame_lbl = ttk.Label(left_frame, text="Customer Information", font=("Poppins", 16, "bold"), foreground="#334155", background="#ffffff")
        cust_frame_lbl.pack(anchor="w", pady=(0,12))

        ttk.Label(left_frame, text="Customer Name:", font=self.normal_font, background="#ffffff").pack(anchor="w", pady=(8,4))
        self.customer_name_var = tk.StringVar()
        customer_entry = ttk.Entry(left_frame, textvariable=self.customer_name_var, font=self.normal_font, width=30)
        customer_entry.pack(anchor="w")

        ttk.Label(left_frame, text="Table Number:", font=self.normal_font, background="#ffffff").pack(anchor="w", pady=(12,4))
        self.table_number_var = tk.StringVar()
        table_entry = ttk.Entry(left_frame, textvariable=self.table_number_var, font=self.normal_font, width=10)
        table_entry.pack(anchor="w")

        # Separator
        ttk.Separator(left_frame, orient="horizontal").pack(fill="x", pady=20)

        # Add Item section
        add_item_lbl = ttk.Label(left_frame, text="Add Item to Order", font=("Poppins", 16, "bold"), background="#ffffff", foreground="#334155")
        add_item_lbl.pack(anchor="w", pady=(0,12))

        ttk.Label(left_frame, text="Select Item:", font=self.normal_font, background="#ffffff").pack(anchor="w", pady=2)
        # Fetch menu items from the MySQL database
        self.menu_items = self.system.get_menu_items()
        self.menu_item_strs = [f"{item.id} - {item.name} - ₹{item.price:.2f}" for item in self.menu_items]

        self.selected_item_var = tk.StringVar()
        self.selected_item_combo = ttk.Combobox(left_frame, textvariable=self.selected_item_var,
                                                values=self.menu_item_strs, font=self.normal_font, width=30,
                                                state="readonly")
        self.selected_item_combo.pack(anchor="w")
        if self.menu_item_strs:
            self.selected_item_combo.current(0) # Select the first item by default

        ttk.Label(left_frame, text="Quantity:", font=self.normal_font, background="#ffffff").pack(anchor="w", pady=6)
        self.quantity_var = tk.IntVar(value=1)
        self.quantity_spin = ttk.Spinbox(left_frame, from_=1, to=100, textvariable=self.quantity_var, width=8, font=self.normal_font)
        self.quantity_spin.pack(anchor="w")

        add_item_btn = ttk.Button(left_frame, text="Add to Order", command=self.add_item_to_order)
        add_item_btn.pack(anchor="w", pady=15)

        # Right side frame: Order summary and place order
        right_frame = ttk.Frame(container, style="Card.TFrame", padding=20)
        right_frame.pack(side="left", fill="both", expand=True, padx=(20,0))

        summary_lbl = ttk.Label(right_frame, text="Order Summary", style="Section.TLabel")
        summary_lbl.pack(anchor="w", pady=(0,10))

        # Treeview displaying current order items
        columns = ("Item", "Quantity", "Unit Price", "Total")
        self.order_tree = ttk.Treeview(right_frame, columns=columns, show="headings", selectmode="browse", height=14)
        for col in columns:
            self.order_tree.heading(col, text=col)
        self.order_tree.column("Item", width=300, anchor="w")
        self.order_tree.column("Quantity", width=80, anchor="center")
        self.order_tree.column("Unit Price", width=100, anchor="e")
        self.order_tree.column("Total", width=110, anchor="e")
        self.order_tree.pack(fill="both", expand=True)

        # Scrollbar for treeview (vertical)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.order_tree.yview)
        self.order_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Remove selected item button
        remove_btn = ttk.Button(right_frame, text="Remove Selected Item", style="Danger.TButton", command=self.remove_selected_order_item)
        remove_btn.pack(pady=10, anchor="e")

        # Subtotal and taxes display
        self.summary_frame = ttk.Frame(right_frame, style="TFrame")
        self.summary_frame.pack(fill="x", pady=(12,10))

        # Payment method selection
        ttk.Label(self.summary_frame, text="Payment Method:", font=("Poppins", 14), background="#ffffff").pack(side="left", pady=4)

        self.payment_method_var = tk.StringVar(value="cash")
        radio_cash = ttk.Radiobutton(self.summary_frame, text="Cash", variable=self.payment_method_var, value="cash")
        radio_card = ttk.Radiobutton(self.summary_frame, text="Card", variable=self.payment_method_var, value="card")
        radio_cash.pack(side="left", padx=8)
        radio_card.pack(side="left", padx=8)

        self.subtotal_label = ttk.Label(self.summary_frame, text="Subtotal: ₹0.00", font=("Poppins", 14, "bold"), background="#ffffff", foreground="#1e293b")
        self.subtotal_label.pack(anchor="e", pady=2)

        self.cgst_label = ttk.Label(self.summary_frame, text="CGST @ 9%: ₹0.00", font=("Poppins", 13), background="#ffffff", foreground="#475569")
        self.cgst_label.pack(anchor="e")

        self.sgst_label = ttk.Label(self.summary_frame, text="SGST @ 9%: ₹0.00", font=("Poppins", 13), background="#ffffff", foreground="#475569")
        self.sgst_label.pack(anchor="e")

        self.total_label = ttk.Label(self.summary_frame, text="Total Amount: ₹0.00", font=("Poppins", 16, "bold"), background="#ffffff", foreground="#2563eb")
        self.total_label.pack(anchor="e", pady=(6,0))

        
        # Submit order button
        place_order_btn = ttk.Button(right_frame, text="Submit Order", command=self.submit_order)
        place_order_btn.pack(pady=15, anchor="center", ipadx=30)

        # Info label for data save status
        self.save_status_var = tk.StringVar()
        save_status_label = ttk.Label(right_frame, textvariable=self.save_status_var, font=("Poppins", 12), foreground="#16a34a", background="#ffffff")
        save_status_label.pack(anchor="center")

        # Focus on customer name entry
        customer_entry.focus_set()

        self.update_order_summary_labels()

    def add_item_to_order(self):
        sel = self.selected_item_var.get()
        if not sel:
            messagebox.showwarning("Input Error", "Please select an item to add.")
            return
        try:
            quantity = self.quantity_var.get()
        except Exception:
            quantity = 1
        if quantity <= 0:
            messagebox.showwarning("Input Error", "Quantity must be at least 1.")
            return

        # Extract item_id from "id - name - price"
        try:
            item_id = int(sel.split(" - ")[0])
        except Exception:
            messagebox.showerror("Error", "Invalid menu item selection.")
            return

        menu_item = next((i for i in self.menu_items if i.id == item_id), None)
        if not menu_item:
            messagebox.showerror("Error", "Selected menu item not found.")
            return

        # Check if item already in order, update qty if so
        found_existing = False
        for oi in self.current_order_items:
            if oi.item_id == item_id:
                oi.quantity += quantity
                found_existing = True
                break
        
        if not found_existing:
            # Use the actual price and name from the fetched menu_item
            new_order_item = OrderItem(item_id=item_id, quantity=quantity, price=menu_item.price, name=menu_item.name)
            self.current_order_items.append(new_order_item)

        self.refresh_order_tree()
        self.update_order_summary_labels()

    def refresh_order_tree(self):
        for row in self.order_tree.get_children():
            self.order_tree.delete(row)

        for idx, item in enumerate(self.current_order_items):
            total_price = item.price * item.quantity
            self.order_tree.insert("", "end", iid=str(idx),
                                   values=(item.name, item.quantity, f"₹{item.price:.2f}", f"₹{total_price:.2f}"))

    def update_order_summary_labels(self):
        subtotal = sum(item.price * item.quantity for item in self.current_order_items)
        cgst = subtotal * (self.system.CGST_RATE / 100)
        sgst = subtotal * (self.system.SGST_RATE / 100)
        total = subtotal + cgst + sgst

        self.subtotal_label.config(text=f"Subtotal: ₹{subtotal:.2f}")
        self.cgst_label.config(text=f"CGST @ {self.system.CGST_RATE}%: ₹{cgst:.2f}")
        self.sgst_label.config(text=f"SGST @ {self.system.SGST_RATE}%: ₹{sgst:.2f}")
        self.total_label.config(text=f"Total Amount: ₹{total:.2f}")

    def remove_selected_order_item(self):
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Select an item to remove from order.")
            return
        idx = int(selected[0]) # Get the iid which is the index
        if 0 <= idx < len(self.current_order_items):
            del self.current_order_items[idx]
            self.refresh_order_tree()
            self.update_order_summary_labels()

    def submit_order(self):
        customer_name = self.customer_name_var.get().strip()
        table_number_str = self.table_number_var.get().strip()
        payment_method = self.payment_method_var.get()

        if not customer_name:
            messagebox.showwarning("Input Error", "Customer name cannot be empty.")
            return

        try:
            table_number = int(table_number_str)
            if table_number <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Table number must be a positive integer.")
            return

        if not self.current_order_items:
            messagebox.showwarning("Input Error", "The order must have at least one item.")
            return

        order = Order(
            customer_name=customer_name,
            table_number=table_number,
            items=self.current_order_items,
            payment_method=payment_method
        )

        order_id = self.system.create_order(order)
        if order_id == -1:
            messagebox.showerror("Error", "Failed to create order. Please try again. Check console for details.")
            self.save_status_var.set("Order creation failed.")
            return

        # Verification of data saved will now involve querying MySQL
        try:
            # Attempt to retrieve the order just created
            verified_order = self.system.get_order(order_id)
            if verified_order and len(verified_order.items) == len(self.current_order_items):
                self.save_status_var.set(f"Order #{order_id} saved successfully with {len(self.current_order_items)} items.")
            else:
                self.save_status_var.set(f"Order saved, but verification failed. Order ID: {order_id}")
        except Exception as e:
            self.save_status_var.set(f"Could not verify saved data: {e}")


        created_order = self.system.get_order(order_id)
        bill_text = self.system.generate_bill(created_order) if created_order else "Error fetching order details."
        # Show detailed bill in messagebox
        messagebox.showinfo("Order Created",
                            f"Order #{order_id} created successfully!\n\nPayment Status: completed\nPayment Method: {payment_method}\n\n"
                            f"{bill_text}")

        # Reset form after order
        self.show_new_order_view()


    ##############################################################################
    # ------------------------ VIEW ORDER BY ID ----------------------------------
    ##############################################################################
    def show_view_order_view(self):
        self.clear_main_area()

        title = ttk.Label(self.main_frame, text="View Order By ID", style="Section.TLabel")
        title.pack(anchor="w", pady=(0,20))

        form_frame = ttk.Frame(self.main_frame, style="TFrame")
        form_frame.pack(pady=10, fill="x")

        ttk.Label(form_frame, text="Order ID:", font=self.normal_font, background="#f5f7fa").grid(row=0, column=0, sticky="w", pady=6)
        self.view_order_id_var = tk.StringVar()
        order_id_entry = ttk.Entry(form_frame, textvariable=self.view_order_id_var, font=self.normal_font, width=15)
        order_id_entry.grid(row=0, column=1, sticky="w", padx=5, pady=6)

        view_btn = ttk.Button(form_frame, text="View Order", command=self.view_order_by_id)
        view_btn.grid(row=0, column=2, sticky="w", padx=10, pady=6)

        # Text widget to show the result
        self.order_text = tk.Text(self.main_frame, wrap="word", height=28, width=105, font=("Poppins", 12),
                                  bg="#ffffff", fg="#1e293b", bd=1, relief="solid")
        self.order_text.pack(pady=10, fill="both", expand=True)

        # Scrollbar for text
        scrollbar = ttk.Scrollbar(self.order_text, command=self.order_text.yview)
        self.order_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        order_id_entry.focus_set()

    def view_order_by_id(self):
        order_id_str = self.view_order_id_var.get().strip()
        if not order_id_str.isdigit():
            messagebox.showwarning("Input Error", "Order ID must be a positive integer.")
            self.order_text.delete("1.0", tk.END)
            return
        order_id = int(order_id_str)
        order = self.system.get_order(order_id)
        if not order:
            messagebox.showinfo("Not Found", f"No order found with ID {order_id}.")
            self.order_text.delete("1.0", tk.END)
            return

        bill = self.system.generate_bill(order)
        self.order_text.delete("1.0", tk.END)
        self.order_text.insert(tk.END, bill)


    ##############################################################################
    # ------------------------ DAILY SALES REPORT -------------------------------
    ##############################################################################
    def show_daily_sales_report_view(self):
        self.clear_main_area()

        title = ttk.Label(self.main_frame, text="Daily Sales Report", style="Section.TLabel")
        title.pack(anchor="w", pady=(0,20))

        form_frame = ttk.Frame(self.main_frame, style="TFrame")
        form_frame.pack(pady=10, fill="x")

        ttk.Label(form_frame, text="Date (YYYY-MM-DD):", font=self.normal_font, background="#f5f7fa").grid(row=0, column=0, sticky="w", pady=6)
        self.report_date_var = tk.StringVar()
        date_entry = ttk.Entry(form_frame, textvariable=self.report_date_var, font=self.normal_font, width=15)
        date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=6)
        # Pre-fill with today's date for convenience
        self.report_date_var.set(datetime.date.today().isoformat()) 

        view_btn = ttk.Button(form_frame, text="View Report", command=self.view_daily_sales_report)
        view_btn.grid(row=0, column=2, sticky="w", padx=10, pady=6)

        # Report display frame
        self.report_frame = ttk.Frame(self.main_frame, style="Card.TFrame", padding=20)
        self.report_frame.pack(fill="both", expand=True, pady=15)

        date_entry.focus_set()

    def view_daily_sales_report(self):
        date_text = self.report_date_var.get().strip()
        try:
            date = datetime.date.fromisoformat(date_text)
        except ValueError:
            messagebox.showwarning("Input Error", "Date must be in YYYY-MM-DD format.")
            return

        report = self.system.get_daily_sales_report(date)
        for widget in self.report_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.report_frame, text=f"Sales Report for {report['date']}", style="Section.TLabel", background="#ffffff").pack(anchor="center", pady=(0,20))

        stats = [
            ("Total Orders", report['order_count']),
            ("Sales (Before Tax)", f"₹{report['total_sales_before_tax']:.2f}"),
            (f"CGST ({self.system.CGST_RATE}%)", f"₹{report['total_cgst']:.2f}"),
            (f"SGST ({self.system.SGST_RATE}%)", f"₹{report['total_sgst']:.2f}"),
            (f"Total GST ({self.system.CGST_RATE + self.system.SGST_RATE}%)", f"₹{report['total_gst']:.2f}"),
            ("Net Sales (Including GST)", f"₹{report['net_sales']:.2f}")
        ]

        for label, value in stats:
            frame = ttk.Frame(self.report_frame, style="TFrame")
            frame.pack(fill="x", padx=10, pady=8)
            ttk.Label(frame, text=label + ":", font=("Poppins", 14, "bold"), foreground="#1e293b", background="#ffffff").pack(side="left")
            ttk.Label(frame, text=value, font=("Poppins", 14), foreground="#475569", background="#ffffff").pack(side="right")


    ##############################################################################
    # ------------------------ CUSTOMER HISTORY ---------------------------------
    ##############################################################################
    def show_customer_history_view(self):
        self.clear_main_area()

        title = ttk.Label(self.main_frame, text="Customer Order History", style="Section.TLabel")
        title.pack(anchor="w", pady=(0,20))

        form_frame = ttk.Frame(self.main_frame, style="TFrame")
        form_frame.pack(pady=10, fill="x")

        ttk.Label(form_frame, text="Customer Name:", font=self.normal_font, background="#f5f7fa").grid(row=0, column=0, sticky="w", pady=6)
        self.customer_history_var = tk.StringVar()
        customer_entry = ttk.Entry(form_frame, textvariable=self.customer_history_var, font=self.normal_font, width=30)
        customer_entry.grid(row=0, column=1, sticky="w", padx=5, pady=6)

        view_btn = ttk.Button(form_frame, text="View History", command=self.view_customer_history)
        view_btn.grid(row=0, column=2, sticky="w", padx=10, pady=6)

        # Scrollable text box for results
        self.customer_history_text = tk.Text(self.main_frame, wrap="word", height=28, width=105, font=("Poppins", 12),
                                             bg="#ffffff", fg="#1e293b", bd=1, relief="solid")
        self.customer_history_text.pack(pady=10, fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.customer_history_text, command=self.customer_history_text.yview)
        self.customer_history_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        customer_entry.focus_set()

    def view_customer_history(self):
        customer_name = self.customer_history_var.get().strip()
        if not customer_name:
            messagebox.showwarning("Input Error", "Customer name cannot be empty.")
            return

        orders = self.system.get_customer_orders(customer_name)
        self.customer_history_text.delete("1.0", tk.END)

        if not orders:
            self.customer_history_text.insert(tk.END, "No orders found for this customer.")
            return

        for order in orders:
            self.customer_history_text.insert(tk.END, f"Order #{order['order_id']} - Date: {order['date']}\n")
            self.customer_history_text.insert(tk.END, f"Table: {order['table']}\n\nItems:\n")
            for item in order['items']:
                line = f"- {item['name']} x{item['quantity']} @ ₹{item['price']:.2f} = ₹{item['total']:.2f}\n"
                self.customer_history_text.insert(tk.END, line)
            self.customer_history_text.insert(tk.END, f"\nSubtotal (before GST): ₹{order['subtotal']:.2f}\n")
            self.customer_history_text.insert(tk.END, f"CGST @ {self.system.CGST_RATE}%: ₹{order['cgst_amount']:.2f}\n")
            self.customer_history_text.insert(tk.END, f"SGST @ {self.system.SGST_RATE}%: ₹{order['sgst_amount']:.2f}\n")
            self.customer_history_text.insert(tk.END, f"Total Amount (including GST): ₹{order['total_with_gst']:.2f}\n")
            self.customer_history_text.insert(tk.END, "-"*72 + "\n\n")


def main():
    root = tk.Tk()
    app = CafeBillingGUI(root)
    # Ensure the database connection is closed when the Tkinter app exits
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, app.system))
    root.mainloop()

def on_closing(root, system):
    """Function to call when the Tkinter window is closed."""
    if system and system.db:
        system.db.close_connection()
    root.destroy()


if __name__ == "__main__":
    main()
