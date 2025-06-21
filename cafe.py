import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import mysql.connector
from mysql.connector import Error

# Database Configuration (Modify these based on your MySQL setup)
DB_CONFIG = {
    'host': 'localhost',
    'port': '3306',
    'user': 'root',  # Replace with your MySQL username
    'password': 'root',  # Replace with your MySQL password
    'database': 'chaicoffee_cafe'
}

@dataclass
class MenuItem:
    """Represents a menu item."""
    id: int
    name: str
    price: float
    category: str
    available: bool = True

@dataclass
class OrderItem:
    """Represents an item in an order."""
    item_id: int
    quantity: int
    price: float  # Price at the time of order
    name: str = "" # Name at the time of order

@dataclass
class Order:
    """Represents a customer order."""
    customer_name: str
    table_number: int
    items: List[OrderItem]
    payment_method: str
    status: str = "completed"
    order_time: Optional[datetime.datetime] = None
    id: Optional[int] = None

class MySQLConnector:
    """Handles MySQL database connection and operations."""
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.connection = None
        self.connect()
        self.create_database_and_tables()
        self.insert_initial_data()

    def connect(self):
        """Establishes a connection to the MySQL database."""
        try:
            # Connect without specifying a database first, to create it if it doesn't exist
            self.connection = mysql.connector.connect(
                host=self.db_config['localhost'],
                port=self.db_config['3306'],
                user=self.db_config['root'],
                password=self.db_config['root']
            )
            if self.connection.is_connected():
                cursor = self.connection.cursor()
                # Create database if it doesn't exist
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['chaicoffee_cafe']}")
                cursor.close()
                self.connection.close() # Close and reconnect with the database selected

                # Reconnect with the specific database
                self.connection = mysql.connector.connect(**self.db_config)
                if self.connection.is_connected():
                    print(f"Connected to MySQL database: {self.db_config['chaicoffee_cafe']}")
                else:
                    print("Failed to reconnect to database.")

        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            print("Please ensure MySQL server is running and credentials are correct.")
            print(f"DB Host: {self.db_config['localhost']}, Port: {self.db_config['3306']}, User: {self.db_config['root']}, Password: {self.db_config['root']}")


    def create_database_and_tables(self):
        """Creates tables if they don't exist."""
        if not self.connection or not self.connection.is_connected():
            print("Cannot create tables: No database connection.")
            return

        cursor = self.connection.cursor()
        try:
            # Create menu_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS menu_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    price DECIMAL(10, 2) NOT NULL,
                    category VARCHAR(255),
                    available BOOLEAN DEFAULT TRUE
                )
            """)
            # Create orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_name VARCHAR(255) NOT NULL,
                    table_number INT,
                    order_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'completed',
                    payment_method VARCHAR(50),
                    subtotal DECIMAL(10, 2) NOT NULL,
                    cgst DECIMAL(10, 2) NOT NULL,
                    sgst DECIMAL(10, 2) NOT NULL,
                    total DECIMAL(10, 2) NOT NULL
                )
            """)
            # Create order_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id INT,
                    item_id INT,
                    item_name VARCHAR(255) NOT NULL,
                    quantity INT NOT NULL,
                    unit_price DECIMAL(10, 2) NOT NULL,
                    total_price DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (item_id) REFERENCES menu_items(id) ON DELETE SET NULL
                )
            """)
            self.connection.commit()
            print("Database tables checked/created successfully.")
        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            cursor.close()

    def insert_initial_data(self):
        """Inserts sample menu items if the menu_items table is empty."""
        if not self.connection or not self.connection.is_connected():
            print("Cannot insert initial data: No database connection.")
            return

        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM menu_items")
            if cursor.fetchone()[0] == 0:
                print("Inserting initial menu data...")
                menu_items_data = [
                    ('Tea', 10.0, 'Beverages', True),
                    ('Coffee', 20.0, 'Beverages', True),
                    ('Chocolate Coffee', 50.0, 'Beverages', True),
                    ('Cold Coffee', 80.0, 'Beverages', True),
                    ('Mocha', 80.0, 'Beverages', True),
                    ('Latte', 90.0, 'Beverages', True),
                    ('Espresso', 90.0, 'Beverages', True),
                    ('Cold Coffee with Ice Cream', 100.0, 'Beverages', True),
                    ('Cappuccino', 120.0, 'Beverages', True),
                    ('Americano', 150.0, 'Beverages', True)
                ]
                insert_query = """
                    INSERT INTO menu_items (name, price, category, available)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.executemany(insert_query, menu_items_data)
                self.connection.commit()
                print("Initial menu data inserted.")
            else:
                print("Menu items already exist.")
        except Error as e:
            print(f"Error inserting initial data: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[int]:
        """Executes a DML query (INSERT, UPDATE, DELETE) and returns lastrowid for inserts."""
        if not self.connection or not self.connection.is_connected():
            print("No database connection. Cannot execute query.")
            return None
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.lastrowid if query.strip().upper().startswith("INSERT") else None
        except Error as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()
            return None
        finally:
            cursor.close()

    def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """Fetches all rows from a SELECT query."""
        if not self.connection or not self.connection.is_connected():
            print("No database connection. Cannot fetch data.")
            return []
        
        cursor = self.connection.cursor(dictionary=True) # Returns results as dictionaries
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching all data: {e}")
            return []
        finally:
            cursor.close()

    def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict]:
        """Fetches a single row from a SELECT query."""
        if not self.connection or not self.connection.is_connected():
            print("No database connection. Cannot fetch data.")
            return None
        
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching one data: {e}")
            return None
        finally:
            cursor.close()

    def close_connection(self):
        """Closes the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed.")

class CafeBillingSystem:
    """Main class for cafe billing operations."""
    
    CGST_RATE = 9.0  # 9% Central GST
    SGST_RATE = 9.0  # 9% State GST
    
    def __init__(self) -> None:
        self.db = MySQLConnector(DB_CONFIG)
        # Ensure database connection is active before proceeding
        if not self.db.connection or not self.db.connection.is_connected():
            print("Database connection failed during initialization. Exiting.")
            # Depending on application design, you might raise an exception or handle gracefully
            # For this example, we'll allow it to continue but operations will likely fail.

    def get_menu_items(self) -> List[MenuItem]:
        """Get list of available menu items from the database."""
        query = "SELECT id, name, price, category, available FROM menu_items WHERE available = TRUE"
        menu_data = self.db.fetch_all(query)
        return [
            MenuItem(
                id=item['id'],
                name=item['name'],
                price=float(item['price']),
                category=item['category'],
                available=bool(item['available'])
            )
            for item in menu_data
        ]
    
    def create_order(self, order: Order) -> int:
        """Create a new order and return its ID."""
        if not self.db.connection or not self.db.connection.is_connected():
            print("Database not connected. Cannot create order.")
            return -1

        try:
            # Calculate subtotal and taxes from current menu prices for accuracy
            subtotal = 0.0
            order_items_to_save = []
            
            for item_in_order in order.items:
                # Fetch current item price from DB to avoid discrepancies
                menu_item_query = "SELECT id, name, price FROM menu_items WHERE id = %s"
                menu_item_data = self.db.fetch_one(menu_item_query, (item_in_order.item_id,))
                
                if not menu_item_data:
                    print(f"Error: Menu item with ID {item_in_order.item_id} not found.")
                    return -1 # Or handle as per business logic (e.g., skip item)
                
                actual_price = float(menu_item_data['price'])
                item_total = actual_price * item_in_order.quantity
                subtotal += item_total
                
                order_items_to_save.append({
                    'item_id': item_in_order.item_id,
                    'item_name': menu_item_data['name'], # Use name from DB
                    'quantity': item_in_order.quantity,
                    'unit_price': actual_price,
                    'total_price': item_total
                })

            cgst_amount = subtotal * (self.CGST_RATE / 100)
            sgst_amount = subtotal * (self.SGST_RATE / 100)
            total = subtotal + cgst_amount + sgst_amount

            # Insert into orders table
            order_insert_query = """
                INSERT INTO orders (customer_name, table_number, order_time, status, payment_method, subtotal, cgst, sgst, total)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            order_time = datetime.datetime.now()
            order_params = (
                order.customer_name,
                order.table_number,
                order_time,
                order.status,
                order.payment_method,
                subtotal,
                cgst_amount,
                sgst_amount,
                total
            )
            new_order_id = self.db.execute_query(order_insert_query, order_params)

            if new_order_id is None:
                print("Failed to insert order into database.")
                return -1

            # Insert into order_items table
            order_item_insert_query = """
                INSERT INTO order_items (order_id, item_id, item_name, quantity, unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            for item_data in order_items_to_save:
                item_params = (
                    new_order_id,
                    item_data['item_id'],
                    item_data['item_name'],
                    item_data['quantity'],
                    item_data['unit_price'],
                    item_data['total_price']
                )
                self.db.execute_query(order_item_insert_query, item_params)

            return new_order_id
        except Exception as e:
            print(f"Error creating order: {e}")
            return -1

    def get_order(self, order_id: int) -> Optional[Order]:
        """Retrieve order details by order ID from the database."""
        order_query = "SELECT * FROM orders WHERE id = %s"
        order_data = self.db.fetch_one(order_query, (order_id,))

        if not order_data:
            return None
        
        items_query = "SELECT item_id, quantity, unit_price, item_name FROM order_items WHERE order_id = %s"
        items_data = self.db.fetch_all(items_query, (order_id,))

        items = [
            OrderItem(
                item_id=item['item_id'],
                quantity=item['quantity'],
                price=float(item['unit_price']),
                name=item['item_name']
            )
            for item in items_data
        ]

        return Order(
            id=order_data['id'],
            customer_name=order_data['customer_name'],
            table_number=order_data['table_number'],
            order_time=order_data['order_time'],
            status=order_data['status'],
            payment_method=order_data['payment_method'],
            items=items
        )

    def get_daily_sales_report(self, date: datetime.date) -> Dict[str, float]:
        """Get sales report for a specific date from the database."""
        report = {
            "date": date.isoformat(),
            "order_count": 0,
            "total_sales_before_tax": 0.0,
            "total_cgst": 0.0,
            "total_sgst": 0.0,
            "total_gst": 0.0,
            "net_sales": 0.0
        }

        query = """
            SELECT 
                COUNT(id) AS order_count,
                SUM(subtotal) AS total_sales_before_tax,
                SUM(cgst) AS total_cgst,
                SUM(sgst) AS total_sgst,
                SUM(total) AS net_sales
            FROM orders
            WHERE DATE(order_time) = %s
        """
        # Convert date to string in 'YYYY-MM-DD' format for MySQL DATE comparison
        result = self.db.fetch_one(query, (date.strftime('%Y-%m-%d'),))

        if result and result['order_count'] is not None:
            report['order_count'] = int(result['order_count'])
            report['total_sales_before_tax'] = float(result['total_sales_before_tax'] or 0.0)
            report['total_cgst'] = float(result['total_cgst'] or 0.0)
            report['total_sgst'] = float(result['total_sgst'] or 0.0)
            report['total_gst'] = report['total_cgst'] + report['total_sgst']
            report['net_sales'] = float(result['net_sales'] or 0.0)
        
        return report

    def get_customer_orders(self, customer_name: str) -> List[Dict]:
        """Get order history for the given customer from the database."""
        # First, get all orders for the customer
        orders_query = "SELECT id, table_number, order_time, subtotal, cgst, sgst, total FROM orders WHERE customer_name = %s ORDER BY order_time DESC"
        customer_orders_data = self.db.fetch_all(orders_query, (customer_name,))
        
        if not customer_orders_data:
            return []

        orders_summary = []
        for order_data in customer_orders_data:
            items_query = "SELECT item_name, quantity, unit_price, total_price FROM order_items WHERE order_id = %s"
            order_items_data = self.db.fetch_all(items_query, (order_data['id'],))
            
            items_list = []
            for item in order_items_data:
                items_list.append({
                    'name': item['item_name'],
                    'quantity': int(item['quantity']),
                    'price': float(item['unit_price']),
                    'total': float(item['total_price'])
                })
            
            orders_summary.append({
                'order_id': int(order_data['id']),
                'date': order_data['order_time'].strftime('%Y-%m-%d'),
                'table': int(order_data['table_number']),
                'items': items_list,
                'subtotal': float(order_data['subtotal']),
                'cgst_amount': float(order_data['cgst']),
                'sgst_amount': float(order_data['sgst']),
                'total_with_gst': float(order_data['total'])
            })

        return orders_summary

    def generate_bill(self, order: Order) -> str:
        """Generate a formatted bill string for the order."""
        lines = [
            f"-------- CHAICOFFEE.COM --------",
            f"Order ID: {order.id}",
            f"Customer Name: {order.customer_name}",
            f"Table Number: {order.table_number}",
            f"Order Time: {order.order_time.strftime('%Y-%m-%d %H:%M:%S') if order.order_time else 'N/A'}",
            f"Payment Method: {order.payment_method}",
            f"Status: {order.status}",
            "",
            f"Items:"
        ]

        subtotal = 0.0 # Recalculate from order items to be sure
        for item in order.items:
            line = f"- {item.name} x{item.quantity} @ ₹{item.price:.2f} = ₹{item.price * item.quantity:.2f}"
            lines.append(line)
            subtotal += item.price * item.quantity

        cgst = subtotal * (self.CGST_RATE / 100)
        sgst = subtotal * (self.SGST_RATE / 100)
        total = subtotal + cgst + sgst

        lines.extend([
            "",
            f"Subtotal (before GST): ₹{subtotal:.2f}",
            f"CGST @ {self.CGST_RATE}%: ₹{cgst:.2f}",
            f"SGST @ {self.SGST_RATE}%: ₹{sgst:.2f}",
            f"Total Amount (including GST): ₹{total:.2f}",
            "-"*30
        ])

        return "\n".join(lines)

def main() -> None:
    """Main function to run the console-based billing system (for testing purposes)."""
    # NOTE: For the GUI version, this main function is not directly called.
    # The GUI's __init__ method will create an instance of CafeBillingSystem.
    
    # IMPORTANT: Before running this, ensure you have MySQL server running
    # and you've updated DB_CONFIG with your actual MySQL username and password.
    # You might also need to install the mysql-connector-python package:
    # pip install mysql-connector-python

    try:
        system = CafeBillingSystem()

        while True:
            print("\n=== CHAICOFFEE.COM (Console) ===")
            print("1. Place New Order")
            print("2. View Order")
            print("3. View Daily Sales Report")
            print("4. View Customer History")
            print("5. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                customer_name = input("Customer Name: ").strip()
                if not customer_name:
                    print("Customer name cannot be empty!")
                    continue

                try:
                    table_number = int(input("Table Number: ").strip())
                    if table_number <= 0:
                        print("Table number must be positive!")
                        continue
                except ValueError:
                    print("Invalid table number!")
                    continue

                items: List[OrderItem] = []
                while True:
                    menu_items = system.get_menu_items()
                    if not menu_items:
                        print("No menu items available!")
                        break

                    print("\nAvailable Items:")
                    for item in menu_items:
                        print(f"{item.id}. {item.name} - ₹{item.price:.2f}")

                    item_id_str = input("\nEnter item ID (or 'done' to finish): ").strip().lower()
                    if item_id_str == 'done':
                        if not items:
                            print("Order must have at least one item!")
                            continue
                        break

                    try:
                        item_id = int(item_id_str)
                    except ValueError:
                        print("Invalid item ID!")
                        continue

                    try:
                        quantity = int(input("Quantity: ").strip())
                        if quantity <= 0:
                            print("Quantity must be positive!")
                            continue
                    except ValueError:
                        print("Invalid quantity!")
                        continue

                    selected_item = next((i for i in menu_items if i.id == item_id), None)
                    if not selected_item:
                        print("Item not found!")
                        continue

                    items.append(OrderItem(
                        item_id=selected_item.id,
                        quantity=quantity,
                        price=selected_item.price, # Use the price from the fetched menu item
                        name=selected_item.name # Use the name from the fetched menu item
                    ))

                if not items: # If user entered 'done' without adding any items
                    print("Order cancelled as no items were added.")
                    continue

                payment_method = input("Payment Method (cash/card): ").strip().lower()
                if payment_method not in {'cash', 'card'}:
                    print("Invalid payment method! Must be 'cash' or 'card'")
                    continue

                order = Order(
                    customer_name=customer_name,
                    table_number=table_number,
                    items=items,
                    payment_method=payment_method
                )

                order_id = system.create_order(order)

                if order_id != -1:
                    print(f"\nOrder #{order_id} created successfully!")
                    print("Payment Status: completed")
                    print(f"Payment Method: {payment_method}")
                    created_order = system.get_order(order_id)
                    if created_order:
                        print(system.generate_bill(created_order))
                else:
                    print("Failed to create order. Please try again.")

            elif choice == "2":
                try:
                    order_id = int(input("Enter Order ID: ").strip())
                    order = system.get_order(order_id)
                    if order:
                        print(system.generate_bill(order))
                    else:
                        print("Order not found!")
                except ValueError:
                    print("Invalid Order ID!")

            elif choice == "3":
                date_str = input("Enter date (YYYY-MM-DD): ").strip()
                try:
                    date = datetime.date.fromisoformat(date_str)
                    report = system.get_daily_sales_report(date)
                    print(f"\nSales Report for {report['date']}")
                    print(f"Total Orders: {report['order_count']}")
                    print(f"Sales (Before Tax): ₹{report['total_sales_before_tax']:.2f}")
                    print(f"CGST ({system.CGST_RATE}%): ₹{report['total_cgst']:.2f}")
                    print(f"SGST ({system.SGST_RATE}%): ₹{report['total_sgst']:.2f}")
                    print(f"Total GST ({system.CGST_RATE + system.SGST_RATE}%): ₹{report['total_gst']:.2f}")
                    print(f"Net Sales (Including GST): ₹{report['net_sales']:.2f}")
                except ValueError:
                    print("Invalid date format!")

            elif choice == "4":
                customer_name = input("Enter customer name: ").strip()
                orders = system.get_customer_orders(customer_name)
                if orders:
                    print(f"\nOrder History for {customer_name}:")
                    for order_summary in orders:
                        print(f"\nOrder #{order_summary['order_id']} - Date: {order_summary['date']}")
                        print(f"Table: {order_summary['table']}")
                        print("\nItems:")
                        for item in order_summary['items']:
                            print(f"- {item['name']} x{item['quantity']} @ ₹{item['price']:.2f} = ₹{item['total']:.2f}")
                        print(f"\nSubtotal (before GST): ₹{order_summary['subtotal']:.2f}")
                        print(f"CGST @ {system.CGST_RATE}%: ₹{order_summary['cgst_amount']:.2f}")
                        print(f"SGST @ {system.SGST_RATE}%: ₹{order_summary['sgst_amount']:.2f}")
                        print(f"Total Amount (including GST): ₹{order_summary['total_with_gst']:.2f}")
                else:
                    print("No orders found for this customer.")

            elif choice == "5":
                print("Thank you for using CHAICOFFEE.COM!")
                break
            else:
                print("Invalid choice!")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'system' in locals() and system.db.connection:
            system.db.close_connection()


if __name__ == "__main__":
    main()



# import datetime
# from typing import Dict, List, Optional
# from dataclasses import dataclass
# import mysql.connector
# from mysql.connector import Error
# from decimal import Decimal, getcontext

# # Set precision for Decimal calculations
# getcontext().prec = 10

# # Database Configuration (Modify these based on your MySQL setup)
# DB_CONFIG = {
#     'host': 'localhost',
#     'user': 'root',  # Replace with your MySQL username
#     'password': 'root',  # Replace with your MySQL password
#     'database': 'chaicoffee_cafe'
# }

# @dataclass
# class MenuItem:
#     """Represents a menu item."""
#     id: int
#     name: str
#     price: Decimal  # Changed to Decimal
#     category: str
#     available: bool = True

# @dataclass
# class OrderItem:
#     """Represents an item in an order."""
#     item_id: int
#     quantity: int
#     price: Decimal  # Changed to Decimal (Price at the time of order)
#     name: str = ""  # Name at the time of order

# @dataclass
# class Order:
#     """Represents a customer order."""
#     customer_name: str
#     table_number: int
#     items: List[OrderItem]
#     payment_method: str
#     status: str = "completed"
#     order_time: Optional[datetime.datetime] = None
#     id: Optional[int] = None
#     subtotal: Decimal = Decimal('0.00')  # Added and changed to Decimal
#     cgst: Decimal = Decimal('0.00')      # Added and changed to Decimal
#     sgst: Decimal = Decimal('0.00')      # Added and changed to Decimal
#     total: Decimal = Decimal('0.00')     # Added and changed to Decimal

# class MySQLConnector:
#     """Handles MySQL database connection and operations."""
#     def __init__(self, db_config: Dict):
#         self.db_config = db_config
#         self.connection = None
#         self.connect()
#         self.create_tables()

#     def connect(self):
#         try:
#             # Connect without specifying the database first, to create it if it doesn't exist
#             self.connection = mysql.connector.connect(
#                 host=self.db_config['localhost'],
#                 user=self.db_config['root'],
#                 password=self.db_config['root']
#             )
#             if self.connection.is_connected():
#                 cursor = self.connection.cursor()
#                 # Create database if not exists
#                 cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['chaicoffee_cafe']}")
#                 # Use the database
#                 cursor.execute(f"USE {self.db_config['chaicoffee_cafe']}")
#                 cursor.close()
#                 print(f"Connected to MySQL database: {self.db_config['chaicoffee_cafe']}")
#             else:
#                 print("Failed to establish initial database connection.")
#                 self.connection = None # Ensure connection is None if failed
#         except Error as e:
#             print(f"Error connecting to MySQL: {e}")
#             print("Please ensure MySQL server is running and credentials are correct.")
#             print(f"DB Host: {self.db_config['localhost']}, User: {self.db_config['root']}, Password: {self.db_config['root']}")
#             self.connection = None # Ensure connection is None if failed

#     def close(self):
#         if self.connection and self.connection.is_connected():
#             self.connection.close()
#             print("MySQL connection closed.")

#     def create_tables(self):
#         if not self.connection or not self.connection.is_connected():
#             print("Cannot create tables: No active database connection.")
#             return

#         cursor = self.connection.cursor()
#         try:
#             # Menu Items Table
#             cursor.execute("""
#                 CREATE TABLE IF NOT EXISTS menu_items (
#                     id INT AUTO_INCREMENT PRIMARY KEY,
#                     name VARCHAR(255) NOT NULL UNIQUE,
#                     price DECIMAL(10, 2) NOT NULL,
#                     category VARCHAR(100),
#                     available BOOLEAN DEFAULT TRUE
#                 )
#             """)
#             # Orders Table
#             cursor.execute("""
#                 CREATE TABLE IF NOT EXISTS orders (
#                     id INT AUTO_INCREMENT PRIMARY KEY,
#                     customer_name VARCHAR(255) NOT NULL,
#                     table_number INT,
#                     order_time DATETIME DEFAULT CURRENT_TIMESTAMP,
#                     payment_method VARCHAR(50),
#                     status VARCHAR(50),
#                     subtotal DECIMAL(10, 2) NOT NULL,
#                     cgst_amount DECIMAL(10, 2) NOT NULL,
#                     sgst_amount DECIMAL(10, 2) NOT NULL,
#                     total_with_gst DECIMAL(10, 2) NOT NULL
#                 )
#             """)
#             # Order Items Table (Junction table for orders and menu_items)
#             cursor.execute("""
#                 CREATE TABLE IF NOT EXISTS order_items (
#                     id INT AUTO_INCREMENT PRIMARY KEY,
#                     order_id INT NOT NULL,
#                     item_id INT,
#                     item_name VARCHAR(255) NOT NULL,
#                     unit_price DECIMAL(10, 2) NOT NULL,
#                     quantity INT NOT NULL,
#                     total_price DECIMAL(10, 2) NOT NULL,
#                     FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
#                     FOREIGN KEY (item_id) REFERENCES menu_items(id) ON DELETE SET NULL
#                 )
#             """)
#             self.connection.commit()
#             print("Tables checked/created successfully.")
#             # self.insert_sample_data() # Optionally uncomment for initial data
#         except Error as e:
#             print(f"Error creating tables: {e}")
#         finally:
#             cursor.close()

#     def insert_sample_data(self):
#         if not self.connection or not self.connection.is_connected():
#             print("Cannot insert sample data: No active database connection.")
#             return

#         cursor = self.connection.cursor()
#         try:
#             # Check if menu items already exist
#             cursor.execute("SELECT COUNT(*) FROM menu_items")
#             if cursor.fetchone()[0] == 0:
#                 menu_data = [
#                     ("Espresso", Decimal('3.50'), "Coffee", True),
#                     ("Latte", Decimal('4.20'), "Coffee", True),
#                     ("Cappuccino", Decimal('4.00'), "Coffee", True),
#                     ("Green Tea", Decimal('2.50'), "Tea", True),
#                     ("Black Tea", Decimal('2.30'), "Tea", True),
#                     ("Croissant", Decimal('3.00'), "Pastry", True),
#                     ("Blueberry Muffin", Decimal('3.75'), "Pastry", True),
#                     ("Chicken Sandwich", Decimal('7.00'), "Sandwich", True),
#                     ("Veggie Wrap", Decimal('6.50'), "Wrap", True)
#                 ]
#                 cursor.executemany("INSERT INTO menu_items (name, price, category, available) VALUES (%s, %s, %s, %s)", menu_data)
#                 self.connection.commit()
#                 print("Sample menu data inserted.")
#             else:
#                 print("Menu items already exist. Skipping sample data insertion.")
#         except Error as e:
#             print(f"Error inserting sample data: {e}")
#             self.connection.rollback()
#         finally:
#             cursor.close()

#     def get_all_menu_items(self) -> List[MenuItem]:
#         if not self.connection or not self.connection.is_connected():
#             print("Cannot get menu items: No active database connection.")
#             return []

#         cursor = self.connection.cursor(dictionary=True)
#         try:
#             cursor.execute("SELECT id, name, price, category, available FROM menu_items WHERE available = TRUE")
#             items = []
#             for item in cursor.fetchall():
#                 items.append(MenuItem(
#                     id=item['id'],
#                     name=item['name'],
#                     price=Decimal(item['price']), # Convert to Decimal
#                     category=item['category'],
#                     available=item['available']
#                 ))
#             return items
#         except Error as e:
#             print(f"Error fetching menu items: {e}")
#             return []
#         finally:
#             cursor.close()

#     def get_menu_item_by_id(self, item_id: int) -> Optional[MenuItem]:
#         if not self.connection or not self.connection.is_connected():
#             print("Cannot get menu item by ID: No active database connection.")
#             return None

#         cursor = self.connection.cursor(dictionary=True)
#         try:
#             cursor.execute("SELECT id, name, price, category, available FROM menu_items WHERE id = %s", (item_id,))
#             item_data = cursor.fetchone()
#             if item_data:
#                 return MenuItem(
#                     id=item_data['id'],
#                     name=item_data['name'],
#                     price=Decimal(item_data['price']), # Convert to Decimal
#                     category=item_data['category'],
#                     available=item_data['available']
#                 )
#             return None
#         except Error as e:
#             print(f"Error fetching menu item by ID: {e}")
#             return None
#         finally:
#             cursor.close()

#     def get_menu_item_by_name(self, item_name: str) -> Optional[MenuItem]:
#         if not self.connection or not self.connection.is_connected():
#             print("Cannot get menu item by name: No active database connection.")
#             return None

#         cursor = self.connection.cursor(dictionary=True)
#         try:
#             cursor.execute("SELECT id, name, price, category, available FROM menu_items WHERE name = %s", (item_name,))
#             item_data = cursor.fetchone()
#             if item_data:
#                 return MenuItem(
#                     id=item_data['id'],
#                     name=item_data['name'],
#                     price=Decimal(item_data['price']), # Convert to Decimal
#                     category=item_data['category'],
#                     available=item_data['available']
#                 )
#             return None
#         except Error as e:
#             print(f"Error fetching menu item by name: {e}")
#             return None
#         finally:
#             cursor.close()

#     def save_order(self, order: Order) -> Optional[int]:
#         if not self.connection or not self.connection.is_connected():
#             print("Cannot save order: No active database connection.")
#             return None

#         cursor = self.connection.cursor()
#         try:
#             # Insert into orders table
#             add_order = ("INSERT INTO orders "
#                          "(customer_name, table_number, payment_method, status, subtotal, cgst_amount, sgst_amount, total_with_gst) "
#                          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
#             order_data = (order.customer_name, order.table_number, order.payment_method, order.status,
#                           order.subtotal, order.cgst, order.sgst, order.total) # Use Decimal objects
#             cursor.execute(add_order, order_data)
#             order_id = cursor.lastrowid

#             # Insert into order_items table
#             add_order_item = ("INSERT INTO order_items "
#                               "(order_id, item_id, item_name, unit_price, quantity, total_price) "
#                               "VALUES (%s, %s, %s, %s, %s, %s)")
#             for item in order.items:
#                 item_total_price = item.price * Decimal(item.quantity) # Calculate with Decimal
#                 item_data = (order_id, item.item_id, item.name, item.price, item.quantity, item_total_price) # Use Decimal objects
#                 cursor.execute(add_order_item, item_data)

#             self.connection.commit()
#             print(f"Order {order_id} saved successfully.")
#             return order_id
#         except Error as e:
#             print(f"Error saving order: {e}")
#             self.connection.rollback()
#             return None
#         finally:
#             cursor.close()

#     def get_order_by_id(self, order_id: int) -> Optional[Order]:
#         if not self.connection or not self.connection.is_connected():
#             print("Cannot get order by ID: No active database connection.")
#             return None

#         cursor = self.connection.cursor(dictionary=True)
#         try:
#             # Fetch order details
#             cursor.execute("""
#                 SELECT id, customer_name, table_number, order_time, payment_method, status,
#                        subtotal, cgst_amount, sgst_amount, total_with_gst
#                 FROM orders WHERE id = %s
#             """, (order_id,))
#             order_data = cursor.fetchone()

#             if not order_data:
#                 return None

#             # Fetch order items
#             cursor.execute("""
#                 SELECT item_id, item_name, unit_price, quantity, total_price
#                 FROM order_items WHERE order_id = %s
#             """, (order_id,))
#             item_data = cursor.fetchall()

#             order_items = [
#                 OrderItem(
#                     item_id=item['item_id'],
#                     quantity=item['quantity'],
#                     price=Decimal(item['unit_price']), # Convert to Decimal
#                     name=item['item_name']
#                 ) for item in item_data
#             ]

#             return Order(
#                 id=order_data['id'],
#                 customer_name=order_data['customer_name'],
#                 table_number=order_data['table_number'],
#                 order_time=order_data['order_time'],
#                 payment_method=order_data['payment_method'],
#                 status=order_data['status'],
#                 items=order_items,
#                 subtotal=Decimal(order_data['subtotal']),          # Convert to Decimal
#                 cgst=Decimal(order_data['cgst_amount']),          # Convert to Decimal
#                 sgst=Decimal(order_data['sgst_amount']),          # Convert to Decimal
#                 total=Decimal(order_data['total_with_gst'])        # Convert to Decimal
#             )
#         except Error as e:
#             print(f"Error fetching order by ID: {e}")
#             return None
#         finally:
#             cursor.close()

#     def get_customer_order_history(self, customer_name: str) -> List[Dict]:
#         if not self.connection or not self.connection.is_connected():
#             print("Cannot get customer order history: No active database connection.")
#             return []

#         cursor = self.connection.cursor(dictionary=True)
#         try:
#             cursor.execute("""
#                 SELECT o.id AS order_id, o.customer_name, o.table_number, o.order_time AS date,
#                        o.subtotal, o.cgst_amount, o.sgst_amount, o.total_with_gst,
#                        oi.item_name AS name, oi.quantity, oi.unit_price AS price, oi.total_price AS total
#                 FROM orders o
#                 JOIN order_items oi ON o.id = oi.order_id
#                 WHERE o.customer_name = %s
#                 ORDER BY o.order_time DESC, o.id ASC
#             """, (customer_name,))

#             raw_orders = cursor.fetchall()
#             if not raw_orders:
#                 return []

#             # Group items by order
#             orders_dict = {}
#             for row in raw_orders:
#                 order_id = row['order_id']
#                 if order_id not in orders_dict:
#                     orders_dict[order_id] = {
#                         'order_id': order_id,
#                         'customer_name': row['customer_name'],
#                         'table': row['table_number'],
#                         'date': row['date'].strftime('%Y-%m-%d %H:%M:%S'),
#                         'subtotal': Decimal(row['subtotal']),      # Convert to Decimal
#                         'cgst_amount': Decimal(row['cgst_amount']), # Convert to Decimal
#                         'sgst_amount': Decimal(row['sgst_amount']), # Convert to Decimal
#                         'total_with_gst': Decimal(row['total_with_gst']), # Convert to Decimal
#                         'items': []
#                     }
#                 orders_dict[order_id]['items'].append({
#                     'name': row['name'],
#                     'quantity': row['quantity'],
#                     'price': Decimal(row['price']), # Convert to Decimal
#                     'total': Decimal(row['total'])  # Convert to Decimal
#                 })
#             return list(orders_dict.values())
#         except Error as e:
#             print(f"Error fetching customer order history: {e}")
#             return []
#         finally:
#             cursor.close()

# class CafeBillingSystem:
#     """Manages cafe billing operations including menu, orders, and sales."""
#     CGST_RATE = Decimal('9.0')  # Central Goods and Services Tax (Example: 9%) - Changed to Decimal
#     SGST_RATE = Decimal('9.0')  # State Goods and Services Tax (Example: 9%) - Changed to Decimal

#     def __init__(self) -> None:
#         self.db = MySQLConnector(DB_CONFIG)
#         # Raise an error if connection was not successful
#         if not self.db.connection or not self.db.connection.is_connected():
#             raise ConnectionError("Failed to connect to MySQL database. Please check your DB_CONFIG and ensure MySQL server is running.")

#         self.current_order_items: List[OrderItem] = []
#         self.current_customer_name: str = ""
#         self.current_table_number: int = 0

#     def start_new_order(self, customer_name: str, table_number: int):
#         self.current_customer_name = customer_name
#         self.current_table_number = table_number
#         self.current_order_items = []
#         print(f"New order started for {customer_name} at table {table_number}.")

#     def add_item_to_current_order(self, item_id: int, quantity: int):
#         menu_item = self.db.get_menu_item_by_id(item_id)
#         if not menu_item or not menu_item.available:
#             print(f"Error: Item with ID {item_id} not found or not available.")
#             return False
#         if quantity <= 0:
#             print("Error: Quantity must be at least 1.")
#             return False

#         # Check if item already exists in current order
#         for order_item in self.current_order_items:
#             if order_item.item_id == item_id:
#                 order_item.quantity += quantity
#                 print(f"Added {quantity} more of {menu_item.name} to order.")
#                 return True

#         self.current_order_items.append(OrderItem(
#             item_id=menu_item.id,
#             name=menu_item.name,
#             quantity=quantity,
#             price=menu_item.price # This is Decimal now
#         ))
#         print(f"Added {quantity} x {menu_item.name} to order.")
#         return True

#     def remove_item_from_current_order(self, item_id: int):
#         initial_len = len(self.current_order_items)
#         self.current_order_items = [item for item in self.current_order_items if item.item_id != item_id]
#         if len(self.current_order_items) < initial_len:
#             print(f"Item with ID {item_id} removed from order.")
#             return True
#         print(f"Item with ID {item_id} not found in current order.")
#         return False

#     def calculate_bill(self) -> Dict[str, Decimal]: # Return Dict with Decimal values
#         subtotal = Decimal('0.00')
#         for item_in_order in self.current_order_items:
#             # Fetch actual price from DB to ensure it's up-to-date and exists
#             actual_menu_item = self.db.get_menu_item_by_id(item_in_order.item_id)
#             if actual_menu_item and actual_menu_item.available:
#                 actual_price = actual_menu_item.price # This is Decimal
#                 subtotal += actual_price * Decimal(item_in_order.quantity)
#             else:
#                 # If item is no longer available/found, use the price recorded at time of adding to order
#                 print(f"Warning: Menu item '{item_in_order.name}' (ID: {item_in_order.item_id}) not found or unavailable. Using recorded price.")
#                 subtotal += item_in_order.price * Decimal(item_in_order.quantity)

#         cgst_amount = (subtotal * self.CGST_RATE) / Decimal('100.0')
#         sgst_amount = (subtotal * self.SGST_RATE) / Decimal('100.0')
#         total_with_gst = subtotal + cgst_amount + sgst_amount

#         return {
#             "subtotal": subtotal,
#             "cgst_amount": cgst_amount,
#             "sgst_amount": sgst_amount,
#             "total_with_gst": total_with_gst
#         }

#     def generate_bill(self, payment_method: str = "Cash") -> Optional[Dict[str, Decimal]]: # Return Dict with Decimal values
#         if not self.current_order_items:
#             print("No items in the current order to generate a bill.")
#             return None

#         bill_details = self.calculate_bill()
#         subtotal = bill_details['subtotal']
#         cgst_amount = bill_details['cgst_amount']
#         sgst_amount = bill_details['sgst_amount']
#         total_with_gst = bill_details['total_with_gst']

#         # Create Order object to save to DB
#         order_to_save = Order(
#             customer_name=self.current_customer_name,
#             table_number=self.current_table_number,
#             items=self.current_order_items,
#             payment_method=payment_method,
#             subtotal=subtotal,
#             cgst=cgst_amount,
#             sgst=sgst_amount,
#             total=total_with_gst
#         )

#         order_id = self.db.save_order(order_to_save)
#         if order_id:
#             print("\n--- Bill ---")
#             print(f"Customer: {self.current_customer_name}")
#             print(f"Table: {self.current_table_number}")
#             print("Items:")
#             for item in self.current_order_items:
#                 item_total = item.price * Decimal(item.quantity) # Calculate with Decimal
#                 print(f"- {item.name} x{item.quantity} @ ₹{item.price:.2f} = ₹{item_total:.2f}")
#             print(f"\nSubtotal (before GST): ₹{subtotal:.2f}")
#             print(f"CGST @ {self.CGST_RATE}%: ₹{cgst_amount:.2f}")
#             print(f"SGST @ {self.SGST_RATE}%: ₹{sgst_amount:.2f}")
#             print(f"Total Amount (including GST): ₹{total_with_gst:.2f}")
#             print(f"Payment Method: {payment_method}")
#             print(f"Order ID: {order_id}")
#             print("------------")
#             return {
#                 "order_id": order_id,
#                 "subtotal": subtotal,
#                 "cgst_amount": cgst_amount,
#                 "sgst_amount": sgst_amount,
#                 "total_with_gst": total_with_gst
#             }
#         return None

#     def get_all_menu_items(self) -> List[MenuItem]:
#         return self.db.get_all_menu_items()

#     def get_customer_orders(self, customer_name: str) -> List[Dict]:
#         return self.db.get_customer_order_history(customer_name)

#     def get_total_sales_for_today(self) -> Decimal: # Return Decimal
#         if not self.db.connection or not self.db.connection.is_connected():
#             print("Cannot calculate total sales: No active database connection.")
#             return Decimal('0.00')

#         cursor = self.db.connection.cursor(dictionary=True)
#         try:
#             today_start = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')
#             today_end = datetime.datetime.now().strftime('%Y-%m-%d 23:59:59')

#             cursor.execute("""
#                 SELECT SUM(total_with_gst) AS total_sales_today
#                 FROM orders
#                 WHERE order_time BETWEEN %s AND %s
#             """, (today_start, today_end))
#             result = cursor.fetchone()
#             # Ensure Decimal conversion and handle None result
#             return Decimal(result['total_sales_today'] or '0.00')
#         except Error as e:
#             print(f"Error getting total sales for today: {e}")
#             return Decimal('0.00')
#         finally:
#             cursor.close()

#     def get_daily_sales_report(self) -> List[Dict]:
#         if not self.db.connection or not self.db.connection.is_connected():
#             print("Cannot get daily sales report: No active database connection.")
#             return []

#         cursor = self.db.connection.cursor(dictionary=True)
#         try:
#             # Query to get daily sales, subtotal, and tax amounts
#             cursor.execute("""
#                 SELECT
#                     DATE(order_time) AS sales_date,
#                     SUM(subtotal) AS total_sales_before_tax,
#                     SUM(cgst_amount) AS total_cgst,
#                     SUM(sgst_amount) AS total_sgst,
#                     SUM(total_with_gst) AS total_sales_after_tax
#                 FROM orders
#                 GROUP BY sales_date
#                 ORDER BY sales_date DESC
#             """)
#             report_data = []
#             for row in cursor.fetchall():
#                 report_data.append({
#                     'sales_date': row['sales_date'].strftime('%Y-%m-%d'),
#                     'total_sales_before_tax': Decimal(row['total_sales_before_tax'] or '0.00'),
#                     'total_cgst': Decimal(row['total_cgst'] or '0.00'),
#                     'total_sgst': Decimal(row['total_sgst'] or '0.00'),
#                     'total_sales_after_tax': Decimal(row['total_sales_after_tax'] or '0.00')
#                 })
#             return report_data
#         except Error as e:
#             print(f"Error getting daily sales report: {e}")
#             return []
#         finally:
#             cursor.close()

#     def get_sales_by_category_report(self) -> List[Dict]:
#         if not self.db.connection or not self.db.connection.is_connected():
#             print("Cannot get sales by category report: No active database connection.")
#             return []

#         cursor = self.db.connection.cursor(dictionary=True)
#         try:
#             cursor.execute("""
#                 SELECT mi.category, SUM(oi.total_price) AS total_category_sales
#                 FROM order_items oi
#                 JOIN menu_items mi ON oi.item_id = mi.id
#                 GROUP BY mi.category
#                 ORDER BY total_category_sales DESC
#             """)
#             report_data = []
#             for row in cursor.fetchall():
#                 report_data.append({
#                     'category': row['category'],
#                     'total_category_sales': Decimal(row['total_category_sales'] or '0.00')
#                 })
#             return report_data
#         except Error as e:
#             print(f"Error getting sales by category report: {e}")
#             return []
#         finally:
#             cursor.close()

#     def get_top_selling_items(self, limit: int = 5) -> List[Dict]:
#         if not self.db.connection or not self.db.connection.is_connected():
#             print("Cannot get top selling items: No active database connection.")
#             return []

#         cursor = self.db.connection.cursor(dictionary=True)
#         try:
#             cursor.execute("""
#                 SELECT item_name, SUM(quantity) AS total_quantity_sold
#                 FROM order_items
#                 GROUP BY item_name
#                 ORDER BY total_quantity_sold DESC
#                 LIMIT %s
#             """, (limit,))
#             report_data = []
#             for row in cursor.fetchall():
#                 report_data.append({
#                     'item_name': row['item_name'],
#                     'total_quantity_sold': row['total_quantity_sold']
#                 })
#             return report_data
#         except Error as e:
#             print(f"Error getting top selling items: {e}")
#             return []
#         finally:
#             cursor.close()

# if __name__ == '__main__':
#     try:
#         system = CafeBillingSystem()
#         # Insert sample data on first run if tables are empty
#         system.db.insert_sample_data()

#         while True:
#             print("\n--- CHAICOFFEE.COM Billing System ---")
#             print("1. Start New Order")
#             print("2. Add Item to Order")
#             print("3. Remove Item from Order")
#             print("4. Generate Bill")
#             print("5. View Menu")
#             print("6. View Customer Order History")
#             print("7. View Daily Sales Report")
#             print("8. View Sales by Category Report")
#             print("9. View Top Selling Items")
#             print("10. Exit")

#             choice = input("Enter your choice: ")

#             if choice == "1":
#                 customer_name = input("Enter customer name: ")
#                 while not customer_name:
#                     print("Customer name cannot be empty.")
#                     customer_name = input("Enter customer name: ")

#                 table_number_str = input("Enter table number (optional, press Enter to skip): ")
#                 table_number = int(table_number_str) if table_number_str else 0

#                 system.start_new_order(customer_name, table_number)

#             elif choice == "2":
#                 if not system.current_order_items and not system.current_customer_name:
#                     print("Please start a new order first (Choice 1).")
#                     continue
#                 menu_items = system.get_all_menu_items()
#                 if not menu_items:
#                     print("No menu items available.")
#                     continue

#                 print("\n--- Menu Items ---")
#                 for item in menu_items:
#                     print(f"ID: {item.id}, Name: {item.name}, Price: ₹{item.price:.2f}, Category: {item.category}")

#                 try:
#                     item_id = int(input("Enter item ID to add: "))
#                     quantity = int(input("Enter quantity: "))
#                     system.add_item_to_current_order(item_id, quantity)
#                 except ValueError:
#                     print("Invalid input. Please enter a valid number for ID and quantity.")

#             elif choice == "3":
#                 if not system.current_order_items:
#                     print("Current order is empty.")
#                     continue
#                 try:
#                     item_id = int(input("Enter item ID to remove: "))
#                     system.remove_item_from_current_order(item_id)
#                 except ValueError:
#                     print("Invalid input. Please enter a valid number for item ID.")

#             elif choice == "4":
#                 if not system.current_order_items:
#                     print("No items in the current order to generate a bill.")
#                     continue
#                 payment_method = input("Enter payment method (e.g., Cash, Card, UPI): ")
#                 bill_info = system.generate_bill(payment_method)
#                 if bill_info:
#                     # Clear current order after successful billing
#                     system.current_order_items = []
#                     system.current_customer_name = ""
#                     system.current_table_number = 0

#             elif choice == "5":
#                 menu_items = system.get_all_menu_items()
#                 if menu_items:
#                     print("\n--- Current Menu ---")
#                     for item in menu_items:
#                         print(f"ID: {item.id}, Name: {item.name}, Price: ₹{item.price:.2f}, Category: {item.category}, Available: {item.available}")
#                 else:
#                     print("No menu items available.")

#             elif choice == "6":
#                 customer_name = input("Enter customer name to view order history: ")
#                 if not customer_name:
#                     print("Customer name cannot be empty.")
#                     continue
#                 orders = system.get_customer_orders(customer_name)
#                 if orders:
#                     print(f"\nOrder History for {customer_name}:")
#                     for order_summary in orders:
#                         print(f"\nOrder #{order_summary['order_id']} - Date: {order_summary['date']}")
#                         print(f"Table: {order_summary['table']}")
#                         print("Items:")
#                         for item in order_summary['items']:
#                             print(f"- {item['name']} x{item['quantity']} @ ₹{item['price']:.2f} = ₹{item['total']:.2f}")
#                         print(f"\nSubtotal (before GST): ₹{order_summary['subtotal']:.2f}")
#                         print(f"CGST @ {system.CGST_RATE}%: ₹{order_summary['cgst_amount']:.2f}")
#                         print(f"SGST @ {system.SGST_RATE}%: ₹{order_summary['sgst_amount']:.2f}")
#                         print(f"Total Amount (including GST): ₹{order_summary['total_with_gst']:.2f}")
#                 else:
#                     print("No orders found for this customer.")

#             elif choice == "7":
#                 daily_sales = system.get_daily_sales_report()
#                 if daily_sales:
#                     print("\n--- Daily Sales Report ---")
#                     for day in daily_sales:
#                         print(f"Date: {day['sales_date']}, Before Tax: ₹{day['total_sales_before_tax']:.2f}, "
#                               f"CGST: ₹{day['total_cgst']:.2f}, SGST: ₹{day['total_sgst']:.2f}, "
#                               f"Total After Tax: ₹{day['total_sales_after_tax']:.2f}")
#                 else:
#                     print("No daily sales data available.")

#             elif choice == "8":
#                 category_sales = system.get_sales_by_category_report()
#                 if category_sales:
#                     print("\n--- Sales by Category Report ---")
#                     for category in category_sales:
#                         print(f"Category: {category['category']}, Total Sales: ₹{category['total_category_sales']:.2f}")
#                 else:
#                     print("No sales by category data available.")

#             elif choice == "9":
#                 top_items = system.get_top_selling_items()
#                 if top_items:
#                     print("\n--- Top 5 Selling Items ---")
#                     for item in top_items:
#                         print(f"Item: {item['item_name']}, Quantity Sold: {item['total_quantity_sold']}")
#                 else:
#                     print("No top-selling items data available.")

#             elif choice == "10":
#                 print("Thank you for using CHAICOFFEE.COM!")
#                 break
#             else:
#                 print("Invalid choice!")
#     except ConnectionError as ce:
#         print(f"Application failed to start due to: {ce}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     finally:
#         if 'system' in locals() and system.db.connection and system.db.connection.is_connected():
#             system.db.close()
