import inspect
import os
import sys
from playhouse.postgres_ext import (
    PostgresqlDatabase,
    PostgresqlExtDatabase,
    Model,
    AutoField,
    CharField,
    IntegerField,
    DoubleField,
    BooleanField,
    DateTimeField,
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
    long_description = CharField(null=True)
    image_url = CharField(null=True)
    price = DoubleField()
    is_on_sale = BooleanField(default=False)
    sale_price = DoubleField(null=True)
    quantity = IntegerField(default=0)


    @classmethod
    def prepopulate(cls):  # pragma: nocover
        products = [
            DatabaseProducts(
                id=1,
                name="Standard SSL",
                description="Your standard SSL certificate",
                long_description="A standard SSL certificate for securing your website",
                price=14.99,
                is_on_sale=False,
                sale_price=8.99,
                quantity=0,
            ),
            DatabaseProducts(
                id=2,
                name="Wildcard SSL",
                description="Encrypt any subdomains may exist on the site",
                long_description="A wildcard SSL certificate for securing your website and all its subdomains",
                price=29.99,
                is_on_sale=True,
                sale_price=19.99,
                quantity=10,
            ),
            DatabaseProducts(
                id=3,
                name="Domain - .com",
                description="Purchase a .com domain",
                long_description="A .com domain for your website",
                price=9.99,
                is_on_sale=False,
                quantity=5,
            ),
            DatabaseProducts(
                id=4,
                name="Domain - .org",
                description="Purchase a .org domain",
                long_description="A .org domain for your website",
                price=8.99,
                is_on_sale=False,
                quantity=3,
            ),
            DatabaseProducts(
                id=5,
                name="Domain - .co",
                description="Purchase a .co domain",
                long_description="A .co domain for your website",
                price=8.99,
                is_on_sale=True,
                sale_price=4.99,
                quantity=7,
            ),
            DatabaseProducts(
                id=6,
                name="Domain - .io",
                description="Purchase a .io domain",
                long_description="A popular .io domain, great for tech startups and developer tools",
                price=39.99,
                is_on_sale=False,
                quantity=15,
            ),
            DatabaseProducts(
                id=7,
                name="Domain - .net",
                description="Purchase a .net domain",
                long_description="A trusted .net domain for your network or tech-focused website",
                price=12.99,
                is_on_sale=False,
                quantity=8,
            ),
            DatabaseProducts(
                id=8,
                name="Web Hosting - Basic",
                description="Affordable shared hosting for personal sites",
                long_description="Get your website online with our Basic shared hosting plan. Includes 10 GB storage, 1 website, and free domain for first year.",
                price=5.99,
                is_on_sale=True,
                sale_price=2.99,
                quantity=100,
            ),
            DatabaseProducts(
                id=9,
                name="Web Hosting - Deluxe",
                description="Unlimited websites and storage",
                long_description="Our Deluxe hosting plan gives you unlimited websites, unlimited storage, and a free domain. Perfect for growing businesses.",
                price=8.99,
                is_on_sale=True,
                sale_price=4.99,
                quantity=100,
            ),
            DatabaseProducts(
                id=10,
                name="Web Hosting - Ultimate",
                description="Maximum performance and resources",
                long_description="The Ultimate hosting plan delivers 2x the performance of Deluxe, with enhanced CPU and RAM for high-traffic websites.",
                price=16.99,
                is_on_sale=False,
                quantity=50,
            ),
            DatabaseProducts(
                id=11,
                name="Professional Email",
                description="Business email using your domain name",
                long_description="Look professional with a custom email address that matches your domain. Includes 10 GB mailbox storage per account.",
                price=1.99,
                is_on_sale=False,
                quantity=200,
            ),
            DatabaseProducts(
                id=12,
                name="Website Builder - Basic",
                description="Drag-and-drop site builder, 1 page",
                long_description="Easily create a stunning one-page website with our drag-and-drop builder. No coding required.",
                price=9.99,
                is_on_sale=False,
                quantity=100,
            ),
            DatabaseProducts(
                id=13,
                name="Website Builder - Premium",
                description="Unlimited pages with e-commerce support",
                long_description="Build a full website with unlimited pages, e-commerce capabilities, SEO tools, and analytics — all with our intuitive builder.",
                price=14.99,
                is_on_sale=True,
                sale_price=9.99,
                quantity=100,
            ),
            DatabaseProducts(
                id=14,
                name="Domain Privacy Protection",
                description="Keep your personal info out of WHOIS",
                long_description="Hide your personal contact information from the public WHOIS directory with our Domain Privacy Protection service.",
                price=9.99,
                is_on_sale=False,
                quantity=500,
            ),
            DatabaseProducts(
                id=15,
                name="Managed WordPress",
                description="Hassle-free WordPress hosting",
                long_description="Our Managed WordPress hosting handles updates, backups, and security so you can focus on your content. Includes automatic daily backups.",
                price=19.99,
                is_on_sale=True,
                sale_price=9.99,
                quantity=50,
            ),
        ]
        DatabaseProducts.bulk_create(products)



class DatabaseCartItem(BaseModel):
    id = AutoField(primary_key=True)
    product_id = IntegerField(null=True)
    name = CharField()
    description = CharField(null=True)
    image_url = CharField(null=True)
    price = DoubleField()
    is_on_sale = BooleanField(default=False)
    sale_price = DoubleField(null=True)
    quantity = IntegerField()

class DatabaseWishlistItem(BaseModel):
    id = AutoField(primary_key=True)
    product_id = IntegerField(null=True)
    name = CharField()
    description = CharField(null=True)
    image_url = CharField(null=True)
    price = DoubleField()
    is_on_sale = BooleanField(default=False)
    sale_price = DoubleField(null=True)


class DatabaseOrder(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()
    email = CharField()
    address = CharField()
    city = CharField()
    state = CharField()
    zip_code = CharField()
    total_price = DoubleField()
    created_at = DateTimeField()


class DatabasePromoCode(BaseModel):
    id = AutoField(primary_key=True)
    code = CharField(unique=True)
    discount_percent = DoubleField()  # percentage discount (e.g., 10.0 for 10%)
    is_active = BooleanField(default=True)
    description = CharField(null=True)

    @classmethod
    def prepopulate(cls):  # pragma: nocover
        promo_codes = [
            DatabasePromoCode(
                code="SAVE10",
                discount_percent=10.0,
                is_active=True,
                description="10% off your order"
            ),
            DatabasePromoCode(
                code="SUMMER25",
                discount_percent=25.0,
                is_active=True,
                description="Summer sale - 25% off!"
            ),
            DatabasePromoCode(
                code="FREESHIP",
                discount_percent=5.0,
                is_active=True,
                description="5% off with free shipping"
            ),
        ]
        DatabasePromoCode.bulk_create(promo_codes)


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

        if DatabasePromoCode in table_models:
            print(f"✅ Populating table: {DatabasePromoCode.__name__}")
            DatabasePromoCode.prepopulate()


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
