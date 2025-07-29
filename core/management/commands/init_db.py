from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):
    help = "Initialize all databases with required tables"

    def handle(self, *args, **kwargs):
        queries = {
            'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    email TEXT
                )
            """,
            'products': """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    price REAL
                )
            """,
            'orders': """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER
                )
            """
        }

        for db, query in queries.items():
            cursor = connections[db].cursor()
            cursor.execute(query)
            self.stdout.write(self.style.SUCCESS(f"{db} database initialized."))
