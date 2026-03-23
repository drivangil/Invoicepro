import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InvoicePro.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()
    username = os.environ.get('ADMIN_USERNAME')
    password = os.environ.get('ADMIN_PASSWORD')
    email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

    if not username or not password:
        print("ADMIN_USERNAME or ADMIN_PASSWORD not set. Skipping admin creation.")
        return

    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser: {username}")
        User.objects.create_superuser(username, email, password)
    else:
        print(f"Superuser {username} already exists.")

if __name__ == '__main__':
    create_admin()
