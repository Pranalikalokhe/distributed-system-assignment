# from django.core.management.base import BaseCommand
# from django.db import connections
# import threading

# users_data = [
#     (1, "Alice", "alice@example.com"),
#     (2, "Bob", "bob@example.com"),
#     (3, "Charlie", "charlie@example.com"),
#     (4, "David", "david@example.com"),
#     (5, "Eve", "eve@example.com"),
#     (6, "Frank", "frank@example.com"),
#     (7, "Grace", "grace@example.com"),
#     (8, "Alice", "alice@example.com"),
#     (9, "Henry", "henry@example.com"),
#     (10, "", "jane@example.com"),  # Invalid (name is empty)
# ]

# products_data = [
#     (1, "Laptop", 1000.00),
#     (2, "Smartphone", 700.00),
#     (3, "Headphones", 150.00),
#     (4, "Monitor", 300.00),
#     (5, "Keyboard", 50.00),
#     (6, "Mouse", 30.00),
#     (7, "Laptop", 1000.00),
#     (8, "Smartwatch", 250.00),
#     (9, "Gaming Chair", 500.00),
#     (10, "Earbuds", -50.00),  # Invalid (price negative)
# ]

# orders_data = [
#     (1, 1, 1, 2),
#     (2, 2, 2, 1),
#     (3, 3, 3, 5),
#     (4, 4, 4, 1),
#     (5, 5, 5, 3),
#     (6, 6, 6, 4),
#     (7, 7, 7, 2),
#     (8, 8, 8, 0),   # Invalid (quantity 0)
#     (9, 9, 1, -1),  # Invalid (negative quantity)
#     (10, 10, 11, 2) # Invalid (product 11 doesn't exist)
# ]

# def validate_user(user):
#     id, name, email = user
#     return bool(name) and "@" in email

# def validate_product(product):
#     id, name, price = product
#     return price > 0

# def validate_order(order):
#     id, user_id, product_id, quantity = order
#     return quantity > 0 and user_id <= 9 and product_id <= 10

# def insert_data(db_name, table, data, validator):
#     cursor = connections[db_name].cursor()
#     valid_records = []

#     for record in data:
#         if validator(record):
#             # Check if record already exists
#             cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE id = %s", [record[0]])
#             if cursor.fetchone()[0] == 0:  # Only insert if not already exists
#                 placeholders = ",".join(["%s"] * len(record))
#                 query = f"INSERT INTO {table} VALUES ({placeholders})"
#                 cursor.execute(query, record)
#                 valid_records.append(record)

#     connections[db_name].commit()
#     return valid_records


# class Command(BaseCommand):
#     help = "Insert data concurrently into all databases and display results"

#     def handle(self, *args, **kwargs):
#         results = {}

#         def insert_and_store(db, table, data, validator):
#             results[db] = insert_data(db, table, data, validator)

#         threads = [
#             threading.Thread(target=insert_and_store, args=('users', 'users', users_data, validate_user)),
#             threading.Thread(target=insert_and_store, args=('products', 'products', products_data, validate_product)),
#             threading.Thread(target=insert_and_store, args=('orders', 'orders', orders_data, validate_order)),
#         ]

#         for t in threads:
#             t.start()
#         for t in threads:
#             t.join()

#         # Display results
#         self.stdout.write("\n=== INSERTED DATA ===")
#         for db, records in results.items():
#             self.stdout.write(f"\n{db.upper()} TABLE:")
#             for record in records:
#                 self.stdout.write(str(record))

from django.core.management.base import BaseCommand
from django.db import connections
import threading

# Sample data
users_data = [
    (1, "Alice", "alice@example.com"),
    (2, "Bob", "bob@example.com"),
    (3, "Charlie", "charlie@example.com"),
    (4, "David", "david@example.com"),
    (5, "Eve", "eve@example.com"),
    (6, "Frank", "frank@example.com"),
    (7, "Grace", "grace@example.com"),
    (8, "Alice", "alice@example.com"),
    (9, "Henry", "henry@example.com"),
    (10, "", "jane@example.com"),  # Invalid (empty name)
]

products_data = [
    (1, "Laptop", 1000.00),
    (2, "Smartphone", 700.00),
    (3, "Headphones", 150.00),
    (4, "Monitor", 300.00),
    (5, "Keyboard", 50.00),
    (6, "Mouse", 30.00),
    (7, "Laptop", 1000.00),
    (8, "Smartwatch", 250.00),
    (9, "Gaming Chair", 500.00),
    (10, "Earbuds", -50.00),  # Invalid (negative price)
]

orders_data = [
    (1, 1, 1, 2),
    (2, 2, 2, 1),
    (3, 3, 3, 5),
    (4, 4, 4, 1),
    (5, 5, 5, 3),
    (6, 6, 6, 4),
    (7, 7, 7, 2),
    (8, 8, 8, 0),   # Invalid (quantity 0)
    (9, 9, 1, -1),  # Invalid (negative quantity)
    (10, 10, 11, 2) # Invalid (product doesn't exist)
]

# Validation functions
def validate_user(user):
    id, name, email = user
    return bool(name) and "@" in email

def validate_product(product):
    id, name, price = product
    return price > 0

def validate_order(order):
    id, user_id, product_id, quantity = order
    return quantity > 0 and user_id <= 9 and product_id <= 10

def clear_table(db_name, table):
    """Delete all old records from the table."""
    cursor = connections[db_name].cursor()
    cursor.execute(f"DELETE FROM {table}")
    connections[db_name].commit()

def insert_data(db_name, table, data, validator):
    cursor = connections[db_name].cursor()
    valid_records = []
    skipped_records = []

    for record in data:
        if validator(record):
            placeholders = ",".join(["%s"] * len(record))
            query = f"INSERT INTO {table} VALUES ({placeholders})"
            cursor.execute(query, record)
            valid_records.append(record)
        else:
            skipped_records.append((record, "Failed validation"))

    connections[db_name].commit()
    return valid_records, skipped_records

class Command(BaseCommand):
    help = "Clear old data, insert fresh data into all databases, and display results"

    def handle(self, *args, **kwargs):
        results = {}
        skipped = {}

        def clear_and_insert(db, table, data, validator):
            clear_table(db, table)  # Delete old records
            valid, skipped_records = insert_data(db, table, data, validator)
            results[db] = valid
            skipped[db] = skipped_records

        threads = [
            threading.Thread(target=clear_and_insert, args=('users', 'users', users_data, validate_user)),
            threading.Thread(target=clear_and_insert, args=('products', 'products', products_data, validate_product)),
            threading.Thread(target=clear_and_insert, args=('orders', 'orders', orders_data, validate_order)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Print inserted data
        self.stdout.write("\n=== INSERTED DATA ===")
        for db, records in results.items():
            self.stdout.write(f"\n{db.upper()} TABLE (Inserted):")
            for record in records:
                self.stdout.write(str(record))

        # Print skipped records
        self.stdout.write("\n=== SKIPPED RECORDS ===")
        for db, records in skipped.items():
            self.stdout.write(f"\n{db.upper()} TABLE (Skipped):")
            if records:
                for record, reason in records:
                    self.stdout.write(f"{record} --> {reason}")
            else:
                self.stdout.write("No skipped records")
