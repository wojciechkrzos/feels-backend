from django.core.management.base import BaseCommand
from neomodel import db


class Command(BaseCommand):
    help = 'Clear all data from the Neo4j database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL data from the Neo4j database.\n'
                    'To proceed, run: python manage.py clear_db --confirm'
                )
            )
            return

        self.stdout.write('Clearing all data from Neo4j database...')
        
        try:
            # Delete all nodes and relationships
            query = "MATCH (n) DETACH DELETE n"
            db.cypher_query(query)
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully cleared all data from Neo4j database!'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error clearing database: {e}'
                )
            )
