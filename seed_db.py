import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_db():
    # Clear existing data
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()

    # Create customers
    customer1 = Customer.objects.create(
        name='John Doe', 
        email='john.doe@example.com', 
        phone='123-456-7890'
    )
    customer2 = Customer.objects.create(
        name='Jane Smith', 
        email='jane.smith@example.com', 
        phone='+19876543210'
    )

    # Create products
    laptop = Product.objects.create(name='Laptop', price=1200.00, stock=10)
    mouse = Product.objects.create(name='Mouse', price=25.00, stock=50)
    keyboard = Product.objects.create(name='Keyboard', price=75.00, stock=30)

    # Create an order
    order = Order.objects.create(customer=customer1, total_amount=1300.00)
    order.products.add(laptop, keyboard)

    print("Database seeded successfully!")
    print(f"Created: {Customer.objects.count()} customers")
    print(f"Created: {Product.objects.count()} products")
    print(f"Created: {Order.objects.count()} orders")

if __name__ == '__main__':
    seed_db()