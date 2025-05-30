from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Populate the database with all sample data (feelings and users)'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate database...')
        
        # First seed feelings
        self.stdout.write('Seeding feelings...')
        call_command('seed_feelings')
        
        # Then seed users and content
        self.stdout.write('Seeding users and content...')
        call_command('seed_users')
        
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully populated database with all sample data!\n'
                'Use "python manage.py seed_feelings" to seed only feelings.\n'
                'Use "python manage.py seed_users" to seed only users and content.'
            )
        )
