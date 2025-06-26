# Coffee-Shop-DBMS
The Chaicoffee Cafe Billing and Management System is a full-stack desktop application developed using Python, MySQL, and Tkinter. It is designed to streamline the billing process and manage orders in a cafe setting. The system supports both a command-line interface (for testing) and a graphical user interface (GUI) built with Tkinter.

This project provides a robust, real-time connection to a MySQL database for storing and retrieving data related to menu items, customer orders, and daily sales. It allows cafe staff to place and view orders, generate bills, retrieve customer order history, and generate daily sales reports.

Key Features:
🔹 Menu Management
Auto-creates a menu table with predefined beverages if not present.

Fetches live data for all available items.


Supports categorization and availability flags.

🔹 Order Processing
Create and manage new customer orders.

Calculates subtotal, CGST, SGST, and total with tax.

Stores itemized details for each order.

🔹 Billing
Automatically generates a detailed, formatted bill with all financial breakdowns.

Order status and payment method are tracked.

🔹 Sales Reporting
Daily sales report for a given date including:

Number of orders

Total revenue

CGST, SGST, and overall GST amounts

Net sales

🔹 Customer Order History
Retrieves order history for individual customers.

Displays order items, date, taxes, and total paid.

Technical Stack:
Frontend: Tkinter (Python GUI toolkit)

Backend: Python (OOP-based architecture)

Database: MySQL (via mysql-connector-python)

Libraries: datetime, dataclasses, tkinter, decimal, typing
![Screenshot (7)](https://github.com/user-attachments/assets/1d427a34-afe3-433d-bbc4-a421d2a3b43a)

