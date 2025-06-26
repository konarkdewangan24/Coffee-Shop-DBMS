import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import mysql.connector
from mysql.connector import Error

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
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
                host=self.db_config['host'],
                port=self.db_config.get('port', 3306),
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            if self.connection.is_connected():
                cursor = self.connection.cursor()
                # Create database if it doesn't exist
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['database']}")
                cursor.close()
                self.connection.close() # Close and reconnect with the database selected

                # Reconnect with the specific database
                self.connection = mysql.connector.connect(**self.db_config)
                if self.connection.is_connected():
                    print(f"Connected to MySQL database: {self.db_config['database']}")
                else:
                    print("Failed to reconnect to database.")

        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            print("Please ensure MySQL server is running and credentials are correct.")
            print(f"DB Host: {self.db_config['host']}, Port: {self.db_config['port']}, User: {self.db_config['user']}, Password: {self.db_config['password']}")
            self.connection = None # Set connection to None if it fails

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
            raise ConnectionError("Database connection failed during initialization. Please check DB_CONFIG and MySQL server status.")

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

