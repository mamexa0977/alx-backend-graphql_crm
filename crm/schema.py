import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
import re
from django.db import transaction

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)

class Query(graphene.ObjectType):
    # ✅ Task 3: Filtered queries
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)

# ✅ Task 1 & 2: Mutations start here
class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists.")
        
        if input.phone and not re.match(r"^(\+1)?\d{10}$|^\d{3}-\d{3}-\d{4}$", input.phone):
            raise Exception("Invalid phone number format.")
        
        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        return CreateCustomer(customer=customer, message="Customer created successfully.")

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers_data = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, customers_data):
        created_customers = []
        error_list = []
        
        with transaction.atomic():
            for data in customers_data:
                try:
                    if Customer.objects.filter(email=data.email).exists():
                        raise Exception(f"Email {data.email} already exists.")
                    
                    if data.phone and not re.match(r"^(\+1)?\d{10}$|^\d{3}-\d{3}-\d{4}$", data.phone):
                        raise Exception(f"Invalid phone number format for {data.email}.")
                    
                    customer = Customer.objects.create(
                        name=data.name,
                        email=data.email,
                        phone=data.phone
                    )
                    created_customers.append(customer)
                except Exception as e:
                    error_list.append(str(e))
        
        return BulkCreateCustomers(customers=created_customers, errors=error_list)

class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(default_value=0)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if float(input.price) <= 0:
            raise Exception("Price must be positive.")
        
        if input.stock < 0:
            raise Exception("Stock cannot be negative.")
        
        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock
        )
        return CreateProduct(product=product)

class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID.")
        
        if not input.product_ids:
            raise Exception("At least one product must be selected.")
        
        products = Product.objects.filter(pk__in=input.product_ids)
        if len(products) != len(input.product_ids):
            raise Exception("Invalid product ID(s).")
        
        total_amount = sum(float(p.price) for p in products)
        
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount
        )
        order.products.set(products)
        
        return CreateOrder(order=order)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()