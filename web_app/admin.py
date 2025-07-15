from django.contrib import admin
from .models import (
Farm, FarmSection, WaterTank, CustomUser, SensorReading, PlantType, IrrigationEvent, Alert, FarmEventLog # Ensure all models are imported, especially SensorReading
)

# Register your models here.
# Basic registrations for now:
admin.site.register(CustomUser)
admin.site.register(Farm)
admin.site.register(FarmSection)
admin.site.register(WaterTank)
admin.site.register(PlantType)
admin.site.register(IrrigationEvent)
admin.site.register(Alert)
admin.site.register(FarmEventLog)

# --- Add/Modify this section for SensorReading ---
@admin.register(SensorReading) # This decorator is a cleaner way to register
class SensorReadingAdmin(admin.ModelAdmin):
    # This list_display will fix the previous AttributeError by using correct field names
    list_display = (
        'farm_section',      # Use the correct foreign key field name
        'moisture_level',    # Use the correct moisture field name
        'water_level',       # Add water_level as it's required
        'temperature',
        'humidity',
        'light_intensity',
        'pH_level',
        'timestamp',         # Good to have the timestamp visible
    )
    list_filter = ('farm_section', 'timestamp',) # Allows filtering by section and date
    search_fields = ('farm_section__name',) # Allows searching by the name of the related farm section
    # If you want to make it easier to add/edit SensorReadings in the admin,
    # you can define a fields or fieldsets here.
    # For now, list_display is key.
