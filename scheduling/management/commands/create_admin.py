import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Reset users and create a default admin account."

    def handle(self, *args, **options):
        username = os.getenv("ADMIN_USERNAME", "admin")
        email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        password = os.getenv("ADMIN_PASSWORD", "admin")

        User = get_user_model()
        User.objects.all().delete()

        user = User.objects.create(username=username, email=email, is_staff=True, is_superuser=True)
        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(f"Created admin user '{username}' with the default password.")
        )
