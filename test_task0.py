import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

from alx_backend_graphql.schema import schema

# Test the hello query
result = schema.execute('{ hello }')
print("Task 0 Test Result:", result.data)