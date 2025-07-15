from rest_framework import serializers
from .models import SensorReading, FarmSection, PlantType, Farm # Import necessary models

class SensorReadingSerializer(serializers.ModelSerializer):
    # We might want to make the 'farm_section' field read-only and look up the actual object
    # or simplify how it's provided by the sensor device (e.g., via section_id)
    # For simplicity, initially, let's allow direct lookup by primary key from device

    class Meta:
        model = SensorReading
        fields = '__all__' # Include all fields from the SensorReading model

        # You might exclude 'timestamp' as it's auto_now_add
        # exclude = ['timestamp']

        # Or specify fields explicitly if you only want certain ones
        # fields = ['id', 'farm_section', 'moisture_level', 'temperature',
        #           'humidity', 'light_intensity', 'pH_level', 'water_level']

# You would add serializers for other models as needed, e.g.:
# class FarmSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Farm
#         fields = '__all__'

# class FarmSectionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FarmSection
#         fields = '__all__'
