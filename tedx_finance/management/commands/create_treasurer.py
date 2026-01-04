from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Create a shared treasurer superuser account'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='treasurer',
            help='Username for the treasurer account (default: treasurer)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Treasurer@123',
            help='Password for the treasurer account (default: Treasurer@123)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='treasurer@tedxfinancehub.com',
            help='Email for the treasurer account'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Treasurer user "{username}" already exists!'))
            return

        # Create superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Treasurer',
            last_name='Account'
        )

        # Make sure user is in Treasurer group
        treasurer_group, created = Group.objects.get_or_create(name='Treasurer')
        user.groups.add(treasurer_group)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(self.style.SUCCESS(f'✓ Treasurer superuser created successfully!'))
        self.stdout.write(f'\n📋 Credentials:')
        self.stdout.write(f'   Username: {username}')
        self.stdout.write(f'   Password: {password}')
        self.stdout.write(f'   Email: {email}')
        self.stdout.write(f'\n⚠️  IMPORTANT:')
        self.stdout.write(f'   - Keep these credentials secure')
        self.stdout.write(f'   - This account has full admin access')
        self.stdout.write(f'   - Change password after setup in production')
        self.stdout.write(f'\n✅ Can now login at:')
        self.stdout.write(f'   Admin: http://localhost:8000/admin/')
        self.stdout.write(f'   App: http://localhost:8000/')
