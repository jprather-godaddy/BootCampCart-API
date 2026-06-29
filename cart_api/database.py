__author__ = "Andrew Williamson <axwilliamson@godaddy.com>"

import inspect
import os
import sys
from playhouse.postgres_ext import (
    PostgresqlDatabase,
    PostgresqlExtDatabase,
    Model,
    AutoField,
    CharField,
    DoubleField,
    BooleanField,
    IntegerField,
)

database = os.environ.get("POSTGRES_DB", "bootcamp")
user = os.environ.get("POSTGRES_USER", "bootcamp")
password = os.environ.get("POSTGRES_PASSWORD", "bootcamp")
hostname = os.environ.get("POSTGRES_HOST", "localhost")


ext_db = PostgresqlExtDatabase(database, user=user, password=password, host=hostname)


class BaseModel(Model):
    class Meta:
        database = PostgresqlDatabase(
            database, user=user, password=password, host=hostname, autorollback=True
        )

# creating a table in the database for products with the following fields
class DatabaseProducts(BaseModel):  
    id = AutoField(primary_key=True)
    name = CharField()
    description = CharField(null=True)
    image_url = CharField(null=True)
    price = DoubleField()
    is_on_sale = BooleanField(default=False)
    sale_price = DoubleField(null=True)


    @classmethod
    def prepopulate(cls):  # pragma: nocover
        products = [
            DatabaseProducts(
                id=1,
                name="Standard SSL",
                description="Your standard SSL certificate",
                price=14.99,
                is_on_sale=False,
                sale_price=8.99,
            ),
            DatabaseProducts(
                id=2,
                name="Wildcard SSL",
                description="Encrypt any subdomains may exist on the site",
                price=29.99,
                is_on_sale=True,
                sale_price=19.99,
            ),
            DatabaseProducts(
                id=3,
                name="Domain - .com",
                description="Purchase a .com domain",
                price=9.99,
                is_on_sale=False,
            ),
            DatabaseProducts(
                id=4,
                name="Domain - .org",
                description="Purchase a .org domain",
                price=8.99,
                is_on_sale=False,
            ),
            DatabaseProducts(
                id=5,
                name="Domain - .co",
                description="Purchase a .co domain",
                price=8.99,
                is_on_sale=True,
                sale_price=4.99,
            ),
        ]
        DatabaseProducts.bulk_create(products)


# Excercise 1:
# Define an ORM class called DatabaseCartItem which inherits from BaseModel
# and has the properties and types defined by your swagger spec.
# if neccesary, update EXAMPLE_CART_ITEM in cart_api_tests/test_exercises.py to match
#this will look almost exactly like the DatabaseProducts class above, but with different fields and types for cart

class DatabaseCartItem(BaseModel): 
    id = AutoField(primary_key=True)
    name = CharField()
    price = DoubleField() #this allows for decimal values, which is what we want for price
    quantity = IntegerField() #got this from methods and fields documentation for peewee, we dont use doublefield for quantity because we want whole numbers for quantity, not decimals
   




# BOOTCAMPERS: Don't modify anything below
ALL_MODELS = [
    c_type
    for c_name, c_type in inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if issubclass(c_type, BaseModel) and c_type not in [BaseModel, Model]
]


def init_tables(table_models=None):  # pragma: nocover
    table_models = table_models or ALL_MODELS

    if isinstance(table_models, Model):
        table_models = [table_models]

    with ext_db.connection_context():
        print(
            f"✅ Creating tables: {', '.join(table.__name__ for table in table_models)}"
        )
        ext_db.drop_tables(table_models, cascade=True)
        ext_db.create_tables(table_models)

        if DatabaseProducts in table_models:
            print(f"✅ Populating table: {DatabaseProducts.__name__}")
            DatabaseProducts.prepopulate()


# Create any tables that don't exist
missing_tables = [table for table in ALL_MODELS if not table.table_exists()]
if missing_tables:  # pragma: nocover
    print(
        f"⚠️ Missing DB Tables: {', '.join(table.__name__ for table in missing_tables)} ⚠️"
    )
    init_tables(missing_tables)

# Else if we explicitly want the tables cleared, recreate them
elif os.environ.get("API_CLEAR_DB", False) in [
    "1",
    1,
    True,
    "true",
    "yes",
]:  # pragma: nocover
    print(
        "⛔⚠️⛔⚠️⛔⚠️⛔ API_CLEAR_DB is set to 1, we are recreating all database tables ⛔⚠️⛔⚠️⛔⚠️⛔"
    )
    init_tables()

else:
    print("The tables already exist! Let's rock and roll 🤘")
