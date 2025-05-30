from django.core.management.base import BaseCommand
from apps.core.models import Feeling, FeelingType


class Command(BaseCommand):
    help = 'Populate the database with feelings and feeling types'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate feelings...')
        
        # Create feeling types
        feeling_types_data = [
            {'name': 'high_energy_pleasant', 'description': 'High energy, pleasant emotions'},
            {'name': 'low_energy_pleasant', 'description': 'Low energy, pleasant emotions'},
            {'name': 'high_energy_unpleasant', 'description': 'High energy, unpleasant emotions'},
            {'name': 'low_energy_unpleasant', 'description': 'Low energy, unpleasant emotions'},
        ]
        
        feeling_types = {}
        for ft_data in feeling_types_data:
            feeling_type = FeelingType(
                name=ft_data['name'],
                description=ft_data['description']
            ).save()
            feeling_types[ft_data['name']] = feeling_type
            self.stdout.write(f'Created feeling type: {ft_data["name"]}')
        
        # Create feelings
        feelings_data = [
            # High energy pleasant
            {'name': 'Excited', 'color': '#FF6B35', 'type': 'high_energy_pleasant'},
            {'name': 'Joyful', 'color': '#FFD23F', 'type': 'high_energy_pleasant'},
            {'name': 'Energetic', 'color': '#EE964B', 'type': 'high_energy_pleasant'},
            {'name': 'Enthusiastic', 'color': '#F95738', 'type': 'high_energy_pleasant'},
            
            # Low energy pleasant
            {'name': 'Content', 'color': '#4ECDC4', 'type': 'low_energy_pleasant'},
            {'name': 'Peaceful', 'color': '#45B7D1', 'type': 'low_energy_pleasant'},
            {'name': 'Grateful', 'color': '#96CEB4', 'type': 'low_energy_pleasant'},
            {'name': 'Relaxed', 'color': '#FECA57', 'type': 'low_energy_pleasant'},
            
            # High energy unpleasant
            {'name': 'Anxious', 'color': '#FF6B6B', 'type': 'high_energy_unpleasant'},
            {'name': 'Frustrated', 'color': '#EE5A24', 'type': 'high_energy_unpleasant'},
            {'name': 'Angry', 'color': '#C44569', 'type': 'high_energy_unpleasant'},
            {'name': 'Stressed', 'color': '#F8B500', 'type': 'high_energy_unpleasant'},
            
            # Low energy unpleasant
            {'name': 'Sad', 'color': '#778CA3', 'type': 'low_energy_unpleasant'},
            {'name': 'Lonely', 'color': '#A55EEA', 'type': 'low_energy_unpleasant'},
            {'name': 'Tired', 'color': '#95A5A6', 'type': 'low_energy_unpleasant'},
            {'name': 'Disappointed', 'color': '#74B9FF', 'type': 'low_energy_unpleasant'},
        ]
        
        feelings = {}
        for feeling_data in feelings_data:
            feeling = Feeling(
                name=feeling_data['name'],
                color=feeling_data['color'],
                description=f"A feeling of being {feeling_data['name'].lower()}"
            ).save()
            
            # Connect to feeling type
            feeling_type = feeling_types[feeling_data['type']]
            feeling.feeling_type.connect(feeling_type)
            
            feelings[feeling_data['name']] = feeling
            self.stdout.write(f'Created feeling: {feeling_data["name"]} ({feeling_data["color"]})')
        
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully populated database with:\n'
                f'- {len(feeling_types)} feeling types\n'
                f'- {len(feelings)} feelings'
            )
        )
