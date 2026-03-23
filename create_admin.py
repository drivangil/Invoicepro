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

    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    
    if created:
        print(f"Superuser {username} created successfully.")
    else:
        print(f"Superuser {username} password updated successfully.")

if __name__ == '__main__':
    create_admin()
