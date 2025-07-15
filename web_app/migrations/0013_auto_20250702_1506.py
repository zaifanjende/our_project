from django.db import migrations
from decimal import Decimal

def create_initial_plant_types(apps, schema_editor):
    PlantType = apps.get_model('web_app', 'PlantType')
    plant_data = [
        {"name": "Maize", "min_moisture_threshold": Decimal('50.00'), "optimal_moisture_min": Decimal('60.00'), "optimal_moisture_max": Decimal('75.00')},
        {"name": "Tomato", "min_moisture_threshold": Decimal('55.00'), "optimal_moisture_min": Decimal('65.00'), "optimal_moisture_max": Decimal('80.00')},
        {"name": "Beans", "min_moisture_threshold": Decimal('45.00'), "optimal_moisture_min": Decimal('55.00'), "optimal_moisture_max": Decimal('70.00')},
        {"name": "Rice", "min_moisture_threshold": Decimal('70.00'), "optimal_moisture_min": Decimal('80.00'), "optimal_moisture_max": Decimal('95.00')},
        {"name": "Cabbage", "min_moisture_threshold": Decimal('60.00'), "optimal_moisture_min": Decimal('70.00'), "optimal_moisture_max": Decimal('85.00')},
        {"name": "Carrot", "min_moisture_threshold": Decimal('50.00'), "optimal_moisture_min": Decimal('60.00'), "optimal_moisture_max": Decimal('75.00')},
        {"name": "Spinach", "min_moisture_threshold": Decimal('65.00'), "optimal_moisture_min": Decimal('75.00'), "optimal_moisture_max": Decimal('90.00')},
    ]
    for data in plant_data:
        PlantType.objects.get_or_create(
            plant_name=data['name'],
            defaults={
                'min_moisture_threshold': data['min_moisture_threshold'],
                'optimal_moisture_min': data['optimal_moisture_min'],
                'optimal_moisture_max': data['optimal_moisture_max']
            }
        )

def reverse_initial_plant_types(apps, schema_editor):
    PlantType = apps.get_model('web_app', 'PlantType')
    plant_names = ["Maize", "Tomato", "Beans", "Rice", "Cabbage", "Carrot", "Spinach"]
    PlantType.objects.filter(name__in=plant_names).delete()

class Migration(migrations.Migration):

    dependencies = [
        # --- THIS IS CRITICAL ---
        # Your data migration (0013) depends on your schema migration (0014)
        ('web_app', '0014_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_plant_types, reverse_initial_plant_types),
    ]
