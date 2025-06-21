# import datetime
# import tkinter as tk
# from tkinter import ttk, messagebox
# from tkinter.font import Font
# from typing import List
# # Import the updated CafeBillingSystem which uses MySQL
# from cafe import CafeBillingSystem, OrderItem, Order

# # No longer need pandas or os for file operations in GUI
# # import pandas as pd
# # import os

# class CafeBillingGUI:
#     def __init__(self, root: tk.Tk):
#         self.root = root
#         self.root.title("Cafe Billing System.")
#         self.root.geometry("1100x750")
#         self.root.configure(bg="#f5f7fa")
#         self.root.minsize(900, 650)

#         # Initialize billing system logic (now connected to MySQL)
#         self.system = CafeBillingSystem()
#         # Check if database connection was successful. If not, disable interaction or exit.
#         if not self.system.db.connection or not self.system.db.connection.is_connected():
#             messagebox.showerror("Database Connection Error", 
#                                  "Failed to connect to MySQL database. Please check your DB_CONFIG "
#                                  "in cafe.py and ensure MySQL server is running.")
#             # Disable all interactive elements or close the app
#             self.root.quit() 
#             return

#         # Configure styles
#         self.style = ttk.Style()
#         self.style.theme_use('clam')  # Use clam for better styling
#         self.style.configure("TFrame", background="#f5f7fa")
#         self.style.configure("Card.TFrame", background="#ffffff", relief="raised", borderwidth=1)
#         self.style.configure("Header.TLabel", font=("Poppins", 26, "bold"), foreground="#1e293b", background="#f5f7fa")
#         self.style.configure("Section.TLabel", font=("Poppins", 18, "bold"), foreground="#334155", background="#ffffff")
#         self.style.configure("TLabel", font=("Poppins", 13), foreground="#475569", background="#f5f7fa")
#         self.style.configure("Bold.TLabel", font=("Poppins", 13, "bold"), foreground="#334155", background="#f5f7fa")
#         self.style.configure("TButton",
#                              font=("Poppins", 13, "bold"),
#                              foreground="#ffffff",
#                              background="#2563eb",
#                              padding=8)
#         self.style.map("TButton",
#             foreground=[('pressed', '#ffffff'), ('active', '#e0e7ff')],
#             background=[('pressed', '#1e40af'), ('active', '#3b82f6')]
#         )
#         self.style.configure("Danger.TButton",
#                              font=("Poppins", 11, "bold"),
#                              foreground="#ffffff",
#                              background="#dc2626",
#                              padding=5)
#         self.style.map("Danger.TButton",
#             foreground=[('pressed', '#ffffff'), ('active', '#fee2e2')],
#             background=[('pressed', '#b91c1c'), ('active', '#ef4444')]
#         )
#         self.style.configure("Treeview.Heading", font=("Poppins", 12, "bold"), foreground="#1e293b")
#         self.style.configure("Treeview", font=("Poppins", 12), rowheight=26)

#         # Fonts
#         self.header_font = Font(family="Poppins", size=26, weight="bold")
#         self.section_font = Font(family="Poppins", size=18, weight="bold")
#         self.normal_font = Font(family="Poppins", size=13)

#         # Create UI components
#         self.create_header()
#         self.create_navbar()
#         self.create_main_area()

#         # Internal state for place order
#         self.current_order_items: List[OrderItem] = []

#         # Show default view
#         self.show_new_order_view()

#     def create_header(self):
#         header_frame = ttk.Frame(self.root, style="TFrame")
#         header_frame.pack(fill="x", pady=(15,10), padx=30)
#         header_label = ttk.Label(header_frame, text="Chaicoffee Cafe Billing System", style="Header.TLabel")
#         header_label.pack(side="left", anchor="w")

#     def create_navbar(self):
#         nav_frame = ttk.Frame(self.root, style="TFrame")
#         nav_frame.pack(fill="x", padx=30, pady=(0,20))

#         buttons = [
#             ("Place New Order", self.show_new_order_view),
#             ("View Order", self.show_view_order_view),
#             ("Daily Sales Report", self.show_daily_sales_report_view),
#             ("Customer History", self.show_customer_history_view),
#             ("Exit", self.root.quit),
#         ]

#         for (text, cmd) in buttons:
#             btn = ttk.Button(nav_frame, text=text, command=cmd)
#             btn.pack(side="left", padx=12, pady=5)

#     def create_main_area(self):
#         self.main_frame = ttk.Frame(self.root, style="TFrame")
#         self.main_frame.pack(fill="both", expand=True, padx=30, pady=10)

#     def clear_main_area(self):
#         for widget in self.main_frame.winfo_children():
#             widget.destroy()

#     ##############################################################################
#     # ------------------------ PLACE NEW ORDER VIEW -----------------------------
#     ##############################################################################
#     def show_new_order_view(self):
#         self.clear_main_area()
#         self.current_order_items.clear()

#         title = ttk.Label(self.main_frame, text="Place New Order", style="Section.TLabel")
#         title.pack(anchor="w", pady=(0,20))

#         container = ttk.Frame(self.main_frame, style="TFrame")
#         container.pack(fill="both", expand=True)

#         # Left side frame: Customer info & add item
#         left_frame = ttk.Frame(container, style="Card.TFrame", padding=20)
#         left_frame.pack(side="left", fill="y", expand=False)

#         # Customer Info
#         cust_frame_lbl = ttk.Label(left_frame, text="Customer Information", font=("Poppins", 16, "bold"), foreground="#334155", background="#ffffff")
#         cust_frame_lbl.pack(anchor="w", pady=(0,12))

#         ttk.Label(left_frame, text="Customer Name:", font=self.normal_font, background="#ffffff").pack(anchor="w", pady=(8,4))
#         self.customer_name_var = tk.StringVar()
#         customer_entry = ttk.Entry(left_frame, textvariable=self.customer_name_var, font=self.normal_font, width=30)
#         customer_entry.pack(anchor="w")

#         ttk.Label(left_frame, text="Table Number:", font=self.normal_font, background="#ffffff").pack(anchor="w", pady=(12,4))
#         self.table_number_var = tk.StringVar()
#         table_entry = ttk.Entry(left_frame, textvariable=self.table_number_var, font=self.normal_font, width=10)
#         table_entry.pack(anchor="w")

#         # Separator
#         ttk.Separator(left_frame, orient="horizontal").pack(fill="x", pady=20)

#         # Add Item section
#         add_item_lbl = ttk.Label(left_frame, text="Add Item to Order", font=("Poppins", 16, "bold"), background="#ffffff", foreground="#334155")
#         add_item_lbl.pack(anchor="w", pady=(0,12))

#         ttk.Label(left_frame, text="Select Item:", font=self.normal_font, background="#ffffff").pack(anchor="w", pady=2)
#         # Fetch menu items from the MySQL database
#         self.menu_items = self.system.get_menu_items()
#         self.menu_item_strs = [f"{item.id} - {item.name} - ₹{item.price:.2f}" for item in self.menu_items]

#         self.selected_item_var = tk.StringVar()
#         self.selected_item_combo = ttk.Combobox(left_frame, textvariable=self.selected_item_var,
#                                                 values=self.menu_item_strs, font=self.normal_font, width=30,
#                                                 state="readonly")
#         self.selected_item_combo.pack(anchor="w")
#         if self.menu_item_strs:
#             self.selected_item_combo.current(0) # Select the first item by default

#         ttk.Label(left_frame, text="Quantity:", font=self.normal_font, background="#ffffff").pack(anchor="w", pady=6)
#         self.quantity_var = tk.IntVar(value=1)
#         self.quantity_spin = ttk.Spinbox(left_frame, from_=1, to=100, textvariable=self.quantity_var, width=8, font=self.normal_font)
#         self.quantity_spin.pack(anchor="w")

#         add_item_btn = ttk.Button(left_frame, text="Add to Order", command=self.add_item_to_order)
#         add_item_btn.pack(anchor="w", pady=15)

#         # Right side frame: Order summary and place order
#         right_frame = ttk.Frame(container, style="Card.TFrame", padding=20)
#         right_frame.pack(side="left", fill="both", expand=True, padx=(20,0))

#         summary_lbl = ttk.Label(right_frame, text="Order Summary", style="Section.TLabel")
#         summary_lbl.pack(anchor="w", pady=(0,10))

#         # Treeview displaying current order items
#         columns = ("Item", "Quantity", "Unit Price", "Total")
#         self.order_tree = ttk.Treeview(right_frame, columns=columns, show="headings", selectmode="browse", height=14)
#         for col in columns:
#             self.order_tree.heading(col, text=col)
#         self.order_tree.column("Item", width=300, anchor="w")
#         self.order_tree.column("Quantity", width=80, anchor="center")
#         self.order_tree.column("Unit Price", width=100, anchor="e")
#         self.order_tree.column("Total", width=110, anchor="e")
#         self.order_tree.pack(fill="both", expand=True)

#         # Scrollbar for treeview (vertical)
#         scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.order_tree.yview)
#         self.order_tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side="right", fill="y")

#         # Remove selected item button
#         remove_btn = ttk.Button(right_frame, text="Remove Selected Item", style="Danger.TButton", command=self.remove_selected_order_item)
#         remove_btn.pack(pady=10, anchor="e")

#         # Subtotal and taxes display
#         self.summary_frame = ttk.Frame(right_frame, style="TFrame")
#         self.summary_frame.pack(fill="x", pady=(12,10))

#         self.subtotal_label = ttk.Label(self.summary_frame, text="Subtotal: ₹0.00", font=("Poppins", 14, "bold"), background="#ffffff", foreground="#1e293b")
#         self.subtotal_label.pack(anchor="e", pady=2)

#         self.cgst_label = ttk.Label(self.summary_frame, text="CGST @ 9%: ₹0.00", font=("Poppins", 13), background="#ffffff", foreground="#475569")
#         self.cgst_label.pack(anchor="e")

#         self.sgst_label = ttk.Label(self.summary_frame, text="SGST @ 9%: ₹0.00", font=("Poppins", 13), background="#ffffff", foreground="#475569")
#         self.sgst_label.pack(anchor="e")

#         self.total_label = ttk.Label(self.summary_frame, text="Total Amount: ₹0.00", font=("Poppins", 16, "bold"), background="#ffffff", foreground="#2563eb")
#         self.total_label.pack(anchor="e", pady=(6,0))

#         # Payment method selection
#         payment_frame = ttk.Frame(right_frame, style="TFrame")
#         payment_frame.pack(fill="x", pady=(10, 0))
#         ttk.Label(payment_frame, text="Payment Method:", font=("Poppins", 14), background="#ffffff").pack(anchor="w", pady=4)

#         self.payment_method_var = tk.StringVar(value="cash")
#         radio_cash = ttk.Radiobutton(payment_frame, text="Cash", variable=self.payment_method_var, value="cash")
#         radio_card = ttk.Radiobutton(payment_frame, text="Card", variable=self.payment_method_var, value="card")
#         radio_cash.pack(side="left", padx=8)
#         radio_card.pack(side="left", padx=8)

#         # Submit order button
#         place_order_btn = ttk.Button(right_frame, text="Submit Order", command=self.submit_order)
#         place_order_btn.pack(pady=15, anchor="center", ipadx=30)

#         # Info label for data save status
#         self.save_status_var = tk.StringVar()
#         save_status_label = ttk.Label(right_frame, textvariable=self.save_status_var, font=("Poppins", 12), foreground="#16a34a", background="#ffffff")
#         save_status_label.pack(anchor="center")

#         # Focus on customer name entry
#         customer_entry.focus_set()

#         self.update_order_summary_labels()

#     def add_item_to_order(self):
#         sel = self.selected_item_var.get()
#         if not sel:
#             messagebox.showwarning("Input Error", "Please select an item to add.")
#             return
#         try:
#             quantity = self.quantity_var.get()
#         except Exception:
#             quantity = 1
#         if quantity <= 0:
#             messagebox.showwarning("Input Error", "Quantity must be at least 1.")
#             return

#         # Extract item_id from "id - name - price"
#         try:
#             item_id = int(sel.split(" - ")[0])
#         except Exception:
#             messagebox.showerror("Error", "Invalid menu item selection.")
#             return

#         menu_item = next((i for i in self.menu_items if i.id == item_id), None)
#         if not menu_item:
#             messagebox.showerror("Error", "Selected menu item not found.")
#             return

#         # Check if item already in order, update qty if so
#         found_existing = False
#         for oi in self.current_order_items:
#             if oi.item_id == item_id:
#                 oi.quantity += quantity
#                 found_existing = True
#                 break
        
#         if not found_existing:
#             # Use the actual price and name from the fetched menu_item
#             new_order_item = OrderItem(item_id=item_id, quantity=quantity, price=menu_item.price, name=menu_item.name)
#             self.current_order_items.append(new_order_item)

#         self.refresh_order_tree()
#         self.update_order_summary_labels()

#     def refresh_order_tree(self):
#         for row in self.order_tree.get_children():
#             self.order_tree.delete(row)

#         for idx, item in enumerate(self.current_order_items):
#             total_price = item.price * item.quantity
#             self.order_tree.insert("", "end", iid=str(idx),
#                                    values=(item.name, item.quantity, f"₹{item.price:.2f}", f"₹{total_price:.2f}"))

#     def update_order_summary_labels(self):
#         subtotal = sum(item.price * item.quantity for item in self.current_order_items)
#         cgst = subtotal * (self.system.CGST_RATE / 100)
#         sgst = subtotal * (self.system.SGST_RATE / 100)
#         total = subtotal + cgst + sgst

#         self.subtotal_label.config(text=f"Subtotal: ₹{subtotal:.2f}")
#         self.cgst_label.config(text=f"CGST @ {self.system.CGST_RATE}%: ₹{cgst:.2f}")
#         self.sgst_label.config(text=f"SGST @ {self.system.SGST_RATE}%: ₹{sgst:.2f}")
#         self.total_label.config(text=f"Total Amount: ₹{total:.2f}")

#     def remove_selected_order_item(self):
#         selected = self.order_tree.selection()
#         if not selected:
#             messagebox.showwarning("Selection Error", "Select an item to remove from order.")
#             return
#         idx = int(selected[0]) # Get the iid which is the index
#         if 0 <= idx < len(self.current_order_items):
#             del self.current_order_items[idx]
#             self.refresh_order_tree()
#             self.update_order_summary_labels()

#     def submit_order(self):
#         customer_name = self.customer_name_var.get().strip()
#         table_number_str = self.table_number_var.get().strip()
#         payment_method = self.payment_method_var.get()

#         if not customer_name:
#             messagebox.showwarning("Input Error", "Customer name cannot be empty.")
#             return

#         try:
#             table_number = int(table_number_str)
#             if table_number <= 0:
#                 raise ValueError
#         except ValueError:
#             messagebox.showwarning("Input Error", "Table number must be a positive integer.")
#             return

#         if not self.current_order_items:
#             messagebox.showwarning("Input Error", "The order must have at least one item.")
#             return

#         order = Order(
#             customer_name=customer_name,
#             table_number=table_number,
#             items=self.current_order_items,
#             payment_method=payment_method
#         )

#         order_id = self.system.create_order(order)
#         if order_id == -1:
#             messagebox.showerror("Error", "Failed to create order. Please try again. Check console for details.")
#             self.save_status_var.set("Order creation failed.")
#             return

#         # Verification of data saved will now involve querying MySQL
#         try:
#             # Attempt to retrieve the order just created
#             verified_order = self.system.get_order(order_id)
#             if verified_order and len(verified_order.items) == len(self.current_order_items):
#                 self.save_status_var.set(f"Order #{order_id} saved successfully with {len(self.current_order_items)} items.")
#             else:
#                 self.save_status_var.set(f"Order saved, but verification failed. Order ID: {order_id}")
#         except Exception as e:
#             self.save_status_var.set(f"Could not verify saved data: {e}")


#         created_order = self.system.get_order(order_id)
#         bill_text = self.system.generate_bill(created_order) if created_order else "Error fetching order details."
#         # Show detailed bill in messagebox
#         messagebox.showinfo("Order Created",
#                             f"Order #{order_id} created successfully!\n\nPayment Status: completed\nPayment Method: {payment_method}\n\n"
#                             f"{bill_text}")

#         # Reset form after order
#         self.show_new_order_view()


#     ##############################################################################
#     # ------------------------ VIEW ORDER BY ID ----------------------------------
#     ##############################################################################
#     def show_view_order_view(self):
#         self.clear_main_area()

#         title = ttk.Label(self.main_frame, text="View Order By ID", style="Section.TLabel")
#         title.pack(anchor="w", pady=(0,20))

#         form_frame = ttk.Frame(self.main_frame, style="TFrame")
#         form_frame.pack(pady=10, fill="x")

#         ttk.Label(form_frame, text="Order ID:", font=self.normal_font, background="#f5f7fa").grid(row=0, column=0, sticky="w", pady=6)
#         self.view_order_id_var = tk.StringVar()
#         order_id_entry = ttk.Entry(form_frame, textvariable=self.view_order_id_var, font=self.normal_font, width=15)
#         order_id_entry.grid(row=0, column=1, sticky="w", padx=5, pady=6)

#         view_btn = ttk.Button(form_frame, text="View Order", command=self.view_order_by_id)
#         view_btn.grid(row=0, column=2, sticky="w", padx=10, pady=6)

#         # Text widget to show the result
#         self.order_text = tk.Text(self.main_frame, wrap="word", height=28, width=105, font=("Poppins", 12),
#                                   bg="#ffffff", fg="#1e293b", bd=1, relief="solid")
#         self.order_text.pack(pady=10, fill="both", expand=True)

#         # Scrollbar for text
#         scrollbar = ttk.Scrollbar(self.order_text, command=self.order_text.yview)
#         self.order_text.config(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side="right", fill="y")

#         order_id_entry.focus_set()

#     def view_order_by_id(self):
#         order_id_str = self.view_order_id_var.get().strip()
#         if not order_id_str.isdigit():
#             messagebox.showwarning("Input Error", "Order ID must be a positive integer.")
#             self.order_text.delete("1.0", tk.END)
#             return
#         order_id = int(order_id_str)
#         order = self.system.get_order(order_id)
#         if not order:
#             messagebox.showinfo("Not Found", f"No order found with ID {order_id}.")
#             self.order_text.delete("1.0", tk.END)
#             return

#         bill = self.system.generate_bill(order)
#         self.order_text.delete("1.0", tk.END)
#         self.order_text.insert(tk.END, bill)


#     ##############################################################################
#     # ------------------------ DAILY SALES REPORT -------------------------------
#     ##############################################################################
#     def show_daily_sales_report_view(self):
#         self.clear_main_area()

#         title = ttk.Label(self.main_frame, text="Daily Sales Report", style="Section.TLabel")
#         title.pack(anchor="w", pady=(0,20))

#         form_frame = ttk.Frame(self.main_frame, style="TFrame")
#         form_frame.pack(pady=10, fill="x")

#         ttk.Label(form_frame, text="Date (YYYY-MM-DD):", font=self.normal_font, background="#f5f7fa").grid(row=0, column=0, sticky="w", pady=6)
#         self.report_date_var = tk.StringVar()
#         date_entry = ttk.Entry(form_frame, textvariable=self.report_date_var, font=self.normal_font, width=15)
#         date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=6)
#         # Pre-fill with today's date for convenience
#         self.report_date_var.set(datetime.date.today().isoformat()) 

#         view_btn = ttk.Button(form_frame, text="View Report", command=self.view_daily_sales_report)
#         view_btn.grid(row=0, column=2, sticky="w", padx=10, pady=6)

#         # Report display frame
#         self.report_frame = ttk.Frame(self.main_frame, style="Card.TFrame", padding=20)
#         self.report_frame.pack(fill="both", expand=True, pady=15)

#         date_entry.focus_set()

#     def view_daily_sales_report(self):
#         date_text = self.report_date_var.get().strip()
#         try:
#             date = datetime.date.fromisoformat(date_text)
#         except ValueError:
#             messagebox.showwarning("Input Error", "Date must be in YYYY-MM-DD format.")
#             return

#         report = self.system.get_daily_sales_report(date)
#         for widget in self.report_frame.winfo_children():
#             widget.destroy()

#         ttk.Label(self.report_frame, text=f"Sales Report for {report['date']}", style="Section.TLabel", background="#ffffff").pack(anchor="center", pady=(0,20))

#         stats = [
#             ("Total Orders", report['order_count']),
#             ("Sales (Before Tax)", f"₹{report['total_sales_before_tax']:.2f}"),
#             (f"CGST ({self.system.CGST_RATE}%)", f"₹{report['total_cgst']:.2f}"),
#             (f"SGST ({self.system.SGST_RATE}%)", f"₹{report['total_sgst']:.2f}"),
#             (f"Total GST ({self.system.CGST_RATE + self.system.SGST_RATE}%)", f"₹{report['total_gst']:.2f}"),
#             ("Net Sales (Including GST)", f"₹{report['net_sales']:.2f}")
#         ]

#         for label, value in stats:
#             frame = ttk.Frame(self.report_frame, style="TFrame")
#             frame.pack(fill="x", padx=10, pady=8)
#             ttk.Label(frame, text=label + ":", font=("Poppins", 14, "bold"), foreground="#1e293b", background="#ffffff").pack(side="left")
#             ttk.Label(frame, text=value, font=("Poppins", 14), foreground="#475569", background="#ffffff").pack(side="right")


#     ##############################################################################
#     # ------------------------ CUSTOMER HISTORY ---------------------------------
#     ##############################################################################
#     def show_customer_history_view(self):
#         self.clear_main_area()

#         title = ttk.Label(self.main_frame, text="Customer Order History", style="Section.TLabel")
#         title.pack(anchor="w", pady=(0,20))

#         form_frame = ttk.Frame(self.main_frame, style="TFrame")
#         form_frame.pack(pady=10, fill="x")

#         ttk.Label(form_frame, text="Customer Name:", font=self.normal_font, background="#f5f7fa").grid(row=0, column=0, sticky="w", pady=6)
#         self.customer_history_var = tk.StringVar()
#         customer_entry = ttk.Entry(form_frame, textvariable=self.customer_history_var, font=self.normal_font, width=30)
#         customer_entry.grid(row=0, column=1, sticky="w", padx=5, pady=6)

#         view_btn = ttk.Button(form_frame, text="View History", command=self.view_customer_history)
#         view_btn.grid(row=0, column=2, sticky="w", padx=10, pady=6)

#         # Scrollable text box for results
#         self.customer_history_text = tk.Text(self.main_frame, wrap="word", height=28, width=105, font=("Poppins", 12),
#                                              bg="#ffffff", fg="#1e293b", bd=1, relief="solid")
#         self.customer_history_text.pack(pady=10, fill="both", expand=True)

#         # Scrollbar
#         scrollbar = ttk.Scrollbar(self.customer_history_text, command=self.customer_history_text.yview)
#         self.customer_history_text.config(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side="right", fill="y")

#         customer_entry.focus_set()

#     def view_customer_history(self):
#         customer_name = self.customer_history_var.get().strip()
#         if not customer_name:
#             messagebox.showwarning("Input Error", "Customer name cannot be empty.")
#             return

#         orders = self.system.get_customer_orders(customer_name)
#         self.customer_history_text.delete("1.0", tk.END)

#         if not orders:
#             self.customer_history_text.insert(tk.END, "No orders found for this customer.")
#             return

#         for order in orders:
#             self.customer_history_text.insert(tk.END, f"Order #{order['order_id']} - Date: {order['date']}\n")
#             self.customer_history_text.insert(tk.END, f"Table: {order['table']}\n\nItems:\n")
#             for item in order['items']:
#                 line = f"- {item['name']} x{item['quantity']} @ ₹{item['price']:.2f} = ₹{item['total']:.2f}\n"
#                 self.customer_history_text.insert(tk.END, line)
#             self.customer_history_text.insert(tk.END, f"\nSubtotal (before GST): ₹{order['subtotal']:.2f}\n")
#             self.customer_history_text.insert(tk.END, f"CGST @ {self.system.CGST_RATE}%: ₹{order['cgst_amount']:.2f}\n")
#             self.customer_history_text.insert(tk.END, f"SGST @ {self.system.SGST_RATE}%: ₹{order['sgst_amount']:.2f}\n")
#             self.customer_history_text.insert(tk.END, f"Total Amount (including GST): ₹{order['total_with_gst']:.2f}\n")
#             self.customer_history_text.insert(tk.END, "-"*72 + "\n\n")


# def main():
#     root = tk.Tk()
#     app = CafeBillingGUI(root)
#     # Ensure the database connection is closed when the Tkinter app exits
#     root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, app.system))
#     root.mainloop()

# def on_closing(root, system):
#     """Function to call when the Tkinter window is closed."""
#     if system and system.db:
#         system.db.close_connection()
#     root.destroy()


# if __name__ == "__main__":
#     main()




import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from typing import List
# Import the updated CafeBillingSystem which uses MySQL
from cafe import CafeBillingSystem, OrderItem, Order # Import Order for type hinting if needed
from decimal import Decimal # Import Decimal for type consistency

class CafeBillingGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Cafe Billing System") # Corrected period placement
        self.root.geometry("1100x750")
        self.root.configure(bg="#f5f7fa")
        self.root.minsize(900, 650)

        # Initialize billing system logic (now connected to MySQL)
        try:
            self.system = CafeBillingSystem()
        except ConnectionError as e:
            messagebox.showerror("Database Connection Error", str(e))
            self.root.destroy() # Use destroy to properly close the window
            return

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use clam for better styling
        self.style.configure("TFrame", background="#f5f7fa")
        self.style.configure("TLabel", background="#f5f7fa", font=("Poppins", 10))
        self.style.configure("TButton", font=("Poppins", 10, "bold"), background="#4CAF50", foreground="white") # Example styling
        self.style.map("TButton", background=[('active', '#45a049')]) # Hover effect
        self.style.configure("Treeview", font=("Poppins", 10))
        self.style.configure("Treeview.Heading", font=("Poppins", 10, "bold"))
        self.style.configure("TCombobox", font=("Poppins", 10))

        # Centralize font definitions
        self.title_font = Font(family="Poppins", size=20, weight="bold")
        self.header_font = Font(family="Poppins", size=14, weight="bold")
        self.normal_font = Font(family="Poppins", size=10)
        self.bold_font = Font(family="Poppins", size=10, weight="bold")

        # Variables for form inputs
        self.customer_name_var = tk.StringVar()
        self.table_number_var = tk.IntVar(value=0) # Default to 0 for optional table number
        self.selected_item_var = tk.StringVar()
        self.quantity_var = tk.IntVar(value=1)
        self.payment_method_var = tk.StringVar(value="Cash")
        self.save_status_var = tk.StringVar() # For displaying order save status
        self.search_customer_var = tk.StringVar()

        self.current_order_display_items = [] # List to hold (item_name, quantity, price, total) for display

        self._create_widgets()
        self._load_menu_items()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle window close event

    def _create_widgets(self):
        # Main frames
        header_frame = ttk.Frame(self.root, padding="15 15 15 0")
        header_frame.pack(fill=tk.X)

        main_content_frame = ttk.Frame(self.root, padding=15)
        main_content_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        ttk.Label(header_frame, text="CHAICOFFEE.COM Billing System", font=self.title_font, foreground="#333").pack(pady=10)

        # Left Frame: Order Entry
        order_entry_frame = ttk.LabelFrame(main_content_frame, text="New Order", padding=15, style="TFrame")
        order_entry_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(order_entry_frame, text="Customer Name:", font=self.normal_font).grid(row=0, column=0, pady=5, sticky="w")
        ttk.Entry(order_entry_frame, textvariable=self.customer_name_var, font=self.normal_font).grid(row=0, column=1, pady=5, sticky="ew")

        ttk.Label(order_entry_frame, text="Table Number (Optional):", font=self.normal_font).grid(row=1, column=0, pady=5, sticky="w")
        table_spinbox = ttk.Spinbox(order_entry_frame, from_=0, to=999, textvariable=self.table_number_var, width=5, font=self.normal_font)
        table_spinbox.grid(row=1, column=1, pady=5, sticky="w")

        ttk.Separator(order_entry_frame, orient="horizontal").grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        ttk.Label(order_entry_frame, text="Select Item:", font=self.normal_font).grid(row=3, column=0, pady=5, sticky="w")
        self.selected_item_combo = ttk.Combobox(order_entry_frame, textvariable=self.selected_item_var, state="readonly", font=self.normal_font)
        self.selected_item_combo.grid(row=3, column=1, pady=5, sticky="ew")
        self.selected_item_combo.bind("<<ComboboxSelected>>", self._on_item_selected)

        ttk.Label(order_entry_frame, text="Quantity:", font=self.normal_font).grid(row=4, column=0, pady=5, sticky="w")
        quantity_spinbox = ttk.Spinbox(order_entry_frame, from_=1, to=100, textvariable=self.quantity_var, width=5, font=self.normal_font)
        quantity_spinbox.grid(row=4, column=1, pady=5, sticky="w")

        add_item_btn = ttk.Button(order_entry_frame, text="Add Item to Order", command=self._add_item_to_order)
        add_item_btn.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

        # Current Order Display (Treeview)
        ttk.Label(order_entry_frame, text="Current Order:", font=self.header_font).grid(row=6, column=0, columnspan=2, pady=(10,5), sticky="w")
        self.order_tree = ttk.Treeview(order_entry_frame, columns=("Item", "Quantity", "Price", "Total"), show="headings", height=8)
        self.order_tree.heading("Item", text="Item")
        self.order_tree.heading("Quantity", text="Quantity")
        self.order_tree.heading("Price", text="Unit Price")
        self.order_tree.heading("Total", text="Total")
        self.order_tree.column("Item", width=150)
        self.order_tree.column("Quantity", width=70, anchor="center")
        self.order_tree.column("Price", width=80, anchor="e")
        self.order_tree.column("Total", width=90, anchor="e")
        self.order_tree.grid(row=7, column=0, columnspan=2, sticky="nsew", pady=5)

        # Scrollbar for Treeview
        tree_scrollbar = ttk.Scrollbar(order_entry_frame, orient="vertical", command=self.order_tree.yview)
        tree_scrollbar.grid(row=7, column=2, sticky="ns")
        self.order_tree.configure(yscrollcommand=tree_scrollbar.set)

        remove_item_btn = ttk.Button(order_entry_frame, text="Remove Selected Item", command=self._remove_item_from_order)
        remove_item_btn.grid(row=8, column=0, columnspan=2, pady=5, sticky="ew")

        ttk.Separator(order_entry_frame, orient="horizontal").grid(row=9, column=0, columnspan=2, pady=10, sticky="ew")

        # Bill Calculation
        bill_frame = ttk.Frame(order_entry_frame, style="TFrame")
        bill_frame.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(5,0))

        ttk.Label(bill_frame, text="Subtotal (Excl. GST):", font=self.bold_font).grid(row=0, column=0, sticky="w")
        self.subtotal_label = ttk.Label(bill_frame, text="₹0.00", font=self.normal_font)
        self.subtotal_label.grid(row=0, column=1, sticky="e")

        ttk.Label(bill_frame, text=f"CGST ({self.system.CGST_RATE}%):", font=self.bold_font).grid(row=1, column=0, sticky="w")
        self.cgst_label = ttk.Label(bill_frame, text="₹0.00", font=self.normal_font)
        self.cgst_label.grid(row=1, column=1, sticky="e")

        ttk.Label(bill_frame, text=f"SGST ({self.system.SGST_RATE}%):", font=self.bold_font).grid(row=2, column=0, sticky="w")
        self.sgst_label = ttk.Label(bill_frame, text="₹0.00", font=self.normal_font)
        self.sgst_label.grid(row=2, column=1, sticky="e")

        ttk.Label(bill_frame, text="Total (Incl. GST):", font=self.header_font, foreground="#4CAF50").grid(row=3, column=0, sticky="w", pady=(5,0))
        self.total_label = ttk.Label(bill_frame, text="₹0.00", font=self.header_font, foreground="#4CAF50")
        self.total_label.grid(row=3, column=1, sticky="e", pady=(5,0))

        bill_frame.columnconfigure(1, weight=1) # Allow total column to expand

        ttk.Label(order_entry_frame, text="Payment Method:", font=self.normal_font).grid(row=11, column=0, pady=5, sticky="w")
        payment_methods = ["Cash", "Card", "UPI"]
        self.payment_method_combo = ttk.Combobox(order_entry_frame, textvariable=self.payment_method_var, values=payment_methods, state="readonly", font=self.normal_font)
        self.payment_method_combo.grid(row=11, column=1, pady=5, sticky="ew")
        self.payment_method_combo.current(0) # Set default to Cash

        submit_order_btn = ttk.Button(order_entry_frame, text="Submit Order", command=self._submit_order)
        submit_order_btn.grid(row=12, column=0, columnspan=2, pady=10, sticky="ew")

        ttk.Label(order_entry_frame, textvariable=self.save_status_var, font=self.bold_font, foreground="green").grid(row=13, column=0, columnspan=2, pady=5, sticky="n")

        order_entry_frame.columnconfigure(1, weight=1) # Allow widgets in column 1 to expand
        order_entry_frame.rowconfigure(7, weight=1) # Allow treeview to expand

        # Right Frame: Reports and History
        reports_frame = ttk.LabelFrame(main_content_frame, text="Reports & History", padding=15, style="TFrame")
        reports_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Customer History Section
        ttk.Label(reports_frame, text="Customer Order History:", font=self.header_font).pack(pady=(0, 10), anchor="w")
        ttk.Label(reports_frame, text="Enter Customer Name:", font=self.normal_font).pack(pady=5, anchor="w")
        ttk.Entry(reports_frame, textvariable=self.search_customer_var, font=self.normal_font).pack(fill=tk.X, pady=5)
        ttk.Button(reports_frame, text="Search History", command=self._show_customer_history).pack(fill=tk.X, pady=5)

        self.customer_history_text = tk.Text(reports_frame, height=10, width=40, wrap="word", font=self.normal_font, state="disabled")
        self.customer_history_text.pack(fill=tk.BOTH, expand=True, pady=5)
        history_scrollbar = ttk.Scrollbar(reports_frame, command=self.customer_history_text.yview)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.customer_history_text.config(yscrollcommand=history_scrollbar.set)

        ttk.Separator(reports_frame, orient="horizontal").pack(fill=tk.X, pady=15)

        # Sales Reports Buttons
        ttk.Label(reports_frame, text="Sales Reports:", font=self.header_font).pack(pady=(0, 10), anchor="w")
        ttk.Button(reports_frame, text="View Daily Sales", command=self._show_daily_sales).pack(fill=tk.X, pady=5)
        ttk.Button(reports_frame, text="View Sales by Category", command=self._show_sales_by_category).pack(fill=tk.X, pady=5)
        ttk.Button(reports_frame, text="View Top Selling Items", command=self._show_top_selling_items).pack(fill=tk.X, pady=5)

        main_content_frame.columnconfigure(0, weight=1)
        main_content_frame.columnconfigure(1, weight=1)
        main_content_frame.rowconfigure(0, weight=1)

    def _load_menu_items(self):
        self.menu_items = self.system.get_all_menu_items()
        self.menu_item_strs = [f"{item.name} (₹{item.price:.2f})" for item in self.menu_items]
        self.selected_item_combo['values'] = self.menu_item_strs

        if self.menu_item_strs:
            self.selected_item_combo.current(0)
            self._on_item_selected() # Call once to set default item
        else:
            self.selected_item_combo.set("No items available")
            self.selected_item_combo.config(state="disabled")
            # Optionally disable add item button if no items
            # self.add_item_btn.config(state="disabled")

    def _on_item_selected(self, event=None):
        # This function can be used to update price display if needed, or simply pass
        pass

    def _add_item_to_order(self):
        customer_name = self.customer_name_var.get().strip()
        table_number = self.table_number_var.get()

        if not customer_name:
            messagebox.showwarning("Input Error", "Customer Name cannot be empty.")
            return

        selected_item_str = self.selected_item_var.get()
        if not selected_item_str or selected_item_str == "No items available":
            messagebox.showwarning("Input Error", "Please select a menu item.")
            return

        try:
            quantity = self.quantity_var.get()
            if quantity <= 0:
                messagebox.showwarning("Input Error", "Quantity must be at least 1.")
                return
        except tk.TclError: # Catches non-integer input for spinbox
            messagebox.showwarning("Input Error", "Please enter a valid number for quantity.")
            self.quantity_var.set(1) # Reset to 1
            return

        # Find the selected MenuItem object
        selected_menu_item = next((item for item in self.menu_items if f"{item.name} (₹{item.price:.2f})" == selected_item_str), None)

        if not selected_menu_item:
            messagebox.showerror("Error", "Selected item not found in menu. Please refresh.")
            self._load_menu_items() # Try to reload menu
            return

        # Ensure system knows about the current order context
        if not self.system.current_customer_name or self.system.current_customer_name != customer_name or self.system.current_table_number != table_number:
             self.system.start_new_order(customer_name, table_number)

        success = self.system.add_item_to_current_order(selected_menu_item.id, quantity)
        if success:
            self._update_order_display()
            self._update_bill_summary()
            self.save_status_var.set("") # Clear status message

    def _remove_item_from_order(self):
        selected_item = self.order_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item from the current order to remove.")
            return

        # Get the internal item_id from the stored display items based on the selected row
        idx = self.order_tree.index(selected_item[0])
        if 0 <= idx < len(self.system.current_order_items):
            item_to_remove = self.system.current_order_items[idx]
            success = self.system.remove_item_from_current_order(item_to_remove.item_id)
            if success:
                self._update_order_display()
                self._update_bill_summary()
                self.save_status_var.set("") # Clear status message
        else:
            messagebox.showerror("Error", "Could not identify item for removal.")


    def _update_order_display(self):
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)

        self.current_order_display_items = [] # Reset display list

        for item in self.system.current_order_items:
            total_price = item.price * Decimal(item.quantity) # Use Decimal for calculation
            display_item = (item.name, item.quantity, f"₹{item.price:.2f}", f"₹{total_price:.2f}")
            self.order_tree.insert("", tk.END, values=display_item)
            self.current_order_display_items.append(display_item) # Keep track for potential removal logic if needed

    def _update_bill_summary(self):
        bill_details = self.system.calculate_bill()
        self.subtotal_label.config(text=f"₹{bill_details['subtotal']:.2f}")
        self.cgst_label.config(text=f"₹{bill_details['cgst_amount']:.2f}")
        self.sgst_label.config(text=f"₹{bill_details['sgst_amount']:.2f}")
        self.total_label.config(text=f"₹{bill_details['total_with_gst']:.2f}")

    def _submit_order(self):
        if not self.system.current_order_items:
            messagebox.showwarning("No Items", "The current order is empty. Add items before submitting.")
            return

        # Double check customer name and table number (should be set by _add_item_to_order, but good for final check)
        customer_name = self.customer_name_var.get().strip()
        table_number = self.table_number_var.get()
        if not customer_name:
            messagebox.showwarning("Input Error", "Customer Name cannot be empty for submitting an order.")
            return
        if not self.system.current_customer_name or self.system.current_customer_name != customer_name:
             self.system.start_new_order(customer_name, table_number)


        payment_method = self.payment_method_var.get()
        bill_info = self.system.generate_bill(payment_method)

        if bill_info:
            messagebox.showinfo("Order Submitted",
                                f"Order successfully submitted!\n"
                                f"Order ID: {bill_info['order_id']}\n"
                                f"Total Amount: ₹{bill_info['total_with_gst']:.2f}")
            self.save_status_var.set(f"Order {bill_info['order_id']} saved successfully!")
            self._reset_order_form()
        else:
            messagebox.showerror("Error", "Failed to submit order. Please check console for details.")
            self.save_status_var.set("Failed to save order.")

    def _reset_order_form(self):
        self.customer_name_var.set("")
        self.table_number_var.set(0)
        self.system.current_order_items = [] # Clear internal order
        self.system.current_customer_name = ""
        self.system.current_table_number = 0
        self._update_order_display() # Clear treeview
        self._update_bill_summary() # Reset totals to 0
        self.payment_method_combo.current(0) # Reset payment method
        # self.save_status_var.set("") # Keep status for a bit, maybe clear on next new order

    def _show_customer_history(self):
        customer_name = self.search_customer_var.get().strip()
        if not customer_name:
            messagebox.showwarning("Input Error", "Please enter a customer name to search history.")
            return

        orders = self.system.get_customer_orders(customer_name)
        self.customer_history_text.config(state="normal")
        self.customer_history_text.delete(1.0, tk.END)

        if orders:
            self.customer_history_text.insert(tk.END, f"Order History for {customer_name}:\n\n", "header")
            for order_summary in orders:
                self.customer_history_text.insert(tk.END, f"Order #{order_summary['order_id']} - Date: {order_summary['date']}\n", "bold")
                self.customer_history_text.insert(tk.END, f"Table: {order_summary['table']}\n\n")
                self.customer_history_text.insert(tk.END, "Items:\n")
                for item in order_summary['items']:
                    line = f"- {item['name']} x{item['quantity']} @ ₹{item['price']:.2f} = ₹{item['total']:.2f}\n"
                    self.customer_history_text.insert(tk.END, line)
                self.customer_history_text.insert(tk.END, f"\nSubtotal (before GST): ₹{order_summary['subtotal']:.2f}\n")
                self.customer_history_text.insert(tk.END, f"CGST @ {self.system.CGST_RATE}%: ₹{order_summary['cgst_amount']:.2f}\n")
                self.customer_history_text.insert(tk.END, f"SGST @ {self.system.SGST_RATE}%: ₹{order_summary['sgst_amount']:.2f}\n")
                self.customer_history_text.insert(tk.END, f"Total Amount (including GST): ₹{order_summary['total_with_gst']:.2f}\n")
                self.customer_history_text.insert(tk.END, "-"*72 + "\n\n")
        else:
            self.customer_history_text.insert(tk.END, "No orders found for this customer.\n")
        self.customer_history_text.config(state="disabled")

        # Add tags for formatting (optional, but good for clarity)
        self.customer_history_text.tag_configure("header", font=self.header_font, foreground="#333")
        self.customer_history_text.tag_configure("bold", font=self.bold_font)


    def _show_daily_sales(self):
        daily_sales = self.system.get_daily_sales_report()
        report_text = "--- Daily Sales Report ---\n\n"
        if daily_sales:
            for day in daily_sales:
                report_text += (f"Date: {day['sales_date']}\n"
                                f"  Sales Before Tax: ₹{day['total_sales_before_tax']:.2f}\n"
                                f"  CGST: ₹{day['total_cgst']:.2f}\n"
                                f"  SGST: ₹{day['total_sgst']:.2f}\n"
                                f"  Total After Tax: ₹{day['total_sales_after_tax']:.2f}\n\n")
        else:
            report_text += "No daily sales data available.\n"
        messagebox.showinfo("Daily Sales Report", report_text)

    def _show_sales_by_category(self):
        category_sales = self.system.get_sales_by_category_report()
        report_text = "--- Sales by Category Report ---\n\n"
        if category_sales:
            for category in category_sales:
                report_text += f"Category: {category['category']}, Total Sales: ₹{category['total_category_sales']:.2f}\n"
        else:
            report_text += "No sales by category data available.\n"
        messagebox.showinfo("Sales by Category Report", report_text)

    def _show_top_selling_items(self):
        top_items = self.system.get_top_selling_items()
        report_text = "--- Top 5 Selling Items ---\n\n"
        if top_items:
            for item in top_items:
                report_text += f"Item: {item['item_name']}, Quantity Sold: {item['total_quantity_sold']}\n"
        else:
            report_text += "No top-selling items data available.\n"
        messagebox.showinfo("Top Selling Items Report", report_text)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.system.db.connection and self.system.db.connection.is_connected():
                self.system.db.close() # Close DB connection properly
            self.root.destroy()

def main():
    root = tk.Tk()
    app = CafeBillingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()