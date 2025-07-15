from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

# --- Custom User Model ---
class CustomUser(AbstractUser):
    # You can add any additional fields specific to your users here.
    # For example:
    # phone_number = models.CharField(max_length=15, blank=True, null=True)
    # address = models.CharField(max_length=255, blank=True, null=True)

    # It's good practice to make email unique if it's used for login/identification
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)

    # Corrected Indentation for USER_ROLES:
    USER_ROLES = (
       
        ('farm_owner', 'Farm Owner'),
    )
    user_role = models.CharField(max_length=20, default='farm_owner')


    # If you later encounter errors about related_name clashes (e.g., with admin site),
    # uncomment and use these to specify unique reverse relations:
    # groups = models.ManyToManyField(
    #     'auth.Group',
    #     verbose_name='groups',
    #     blank=True,
    #     help_text='The groups this user belongs to. A user will get all permissions '
    #                 'granted to each of their groups.',
    #     related_name="customuser_groups",
    #     related_query_name="customuser",
    # )
    # user_permissions = models.ManyToManyField(
    #     'auth.Permission',
    #     verbose_name='user permissions',
    #     blank=True,
    #     help_text='Specific permissions for this user.',
    #     related_name="customuser_user_permissions",
    #     related_query_name="customuser",
    # )

def __str__(self):
    return self.username

# --- Farm Model ---
class Farm(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=255)
    # description = models.TextField(blank=True, null=True)
    # The ForeignKey links a Farm to its owner (a CustomUser)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    primary_plant_type = models.ForeignKey(
        'PlantType',
        on_delete=models.SET_NULL, # If a PlantType is deleted, this field can become null
        null=True,
        blank=True,
        related_name='farms_with_this_primary_type',
    )


FARM_STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('pending', 'Pending Setup'),
    )
system_status = models.CharField(max_length=20, choices=FARM_STATUS_CHOICES, default='active')


def __str__(self):
    return self.plant_name

# --- Farm Section Model (e.g., a specific plot within a farm) ---
class FarmSection(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='farm_sections')
    name = models.CharField(max_length=100)
    plant_type = models.CharField(max_length=100, blank=True)
    area_sq_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    sensor_location = models.CharField(max_length=255, blank=True, null=True)
    last_calibrated = models.DateTimeField(null=True, blank=True)

    # This links a FarmSection to a PlantType
    primary_plant_typeplant_type = models.ForeignKey('PlantType', on_delete=models.SET_NULL, null=True, blank=True, related_name='sections')

    
def __str__(self):
    return f"{self.name} ({self.farm.name})"

# --- Water Tank Model ---
class WaterTank(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='water_tanks')
    tank_name = models.CharField(max_length=100)
    pump_is_on = models.BooleanField(default=False)

        # Note: 'total_capacity_litres' seems redundant if 'capacity_liters' exists.
    # I'll add it as requested by your form, but you might want to review if one of them is unnecessary.
    total_capacity_litres = models.IntegerField(null=True, blank=True) # Adding this field as requested by the form
    empty_level_threshold_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    low_level_threshold_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    last_volume_litres = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Sensor related pins and readings
    sensor_pin_trig = models.IntegerField(null=True, blank=True)
    sensor_pin_echo = models.IntegerField(null=True, blank=True)
    last_reading_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    TANK_STATUS_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Error'),
        ('unknown', 'Unknown'),
    )
    status = models.CharField(max_length=20, choices=TANK_STATUS_CHOICES, default='unknown')
       # Note: 'total_capacity_litres' seems redundant if 'capacity_liters' exists.
    # I'll add it as requested by your form, but you might want to review if one of them is unnecessary.

    # Sensor related pins and readings
    sensor_pin_trig = models.IntegerField(null=True, blank=True)
    sensor_pin_echo = models.IntegerField(null=True, blank=True)
    last_reading_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    TANK_STATUS_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Error'),
        ('unknown', 'Unknown'),
    )
    status = models.CharField(max_length=20, choices=TANK_STATUS_CHOICES, default='unknown')
    last_updated = models.DateTimeField(auto_now=True) # Automatically updates on each save

def get_pump_is_on_display(self):
    return "ON" if self.pump_is_on else "OFF"

def __str__(self):
    return f"{self.tank_name} ({self.farm.name})"

# --- Sensor Reading Model ---
class SensorReading(models.Model):
    farm_section = models.ForeignKey(FarmSection, on_delete=models.CASCADE, related_name='sensor_readings')
    moisture_level = models.DecimalField(max_digits=5, decimal_places=2) # e.g., percentage
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # e.g., percentage
    light_intensity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # e.g., in Lux
    pH_level = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True) # pH scale typically 0-14


    SENSOR_STATUS_CHOICES = (
        ('normal', 'Normal'),
        ('alert', 'Alert'),
        ('offline', 'Offline'),
        ('error', 'Error'),
    )
    status = models.CharField(max_length=20, choices=SENSOR_STATUS_CHOICES, default='normal')

    pump_status = models.BooleanField(default=False) # True for ON, False for OFF
    water_level = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True) # General water level reading


    class Meta:
        ordering = ['-timestamp'] # Order by most recent first

def __str__(self):
    return f"Moisture: {self.moisture_level}% in {self.farm_section.name} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

# --- Plant Type Model ---
class PlantType(models.Model):
    plant_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True, null=True)
        
    min_moisture_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Minimum moisture level (%) below which irrigation should be triggered.",
        null=True, blank=True
    )
    optimal_moisture_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Optimal lower bound of moisture level (%).",
        null=True, blank=True
    )
    optimal_moisture_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Optimal upper bound of moisture level (%).",
        null=True, blank=True
    )

    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_plant_types',
                              help_text="The user who created this plant type. Null for global/system-defined types.")
    is_global = models.BooleanField(default=False, help_text="Indicates if this is a system-wide or global plant type.")


def __str__(self):
    return self.plant_name

# You might want to link PlantType to FarmSection, e.g.,
# In FarmSection model, add:
# plant_type = models.ForeignKey(PlantType, on_delete=models.SET_NULL, null=True, blank=True, related_name='sections')


# --- Irrigation Event Model ---
class IrrigationEvent(models.Model):
    section = models.ForeignKey(FarmSection, on_delete=models.CASCADE, related_name='irrigation_events')
    tank = models.ForeignKey(
        'WaterTank', # Use lazy reference if WaterTank is defined later
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='irrigation_events' # Changed related_name
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    # New fields from your list
    start_moisture = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    end_moisture = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    start_tank_volume = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    end_tank_volume = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    duration_seconds = models.IntegerField(null=True, blank=True)
    water_volume_dispensed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Renamed from water_applied_liters

    TRIGGER_REASON_CHOICES = (
        ('schedule', 'Scheduled'),
        ('manual', 'Manual Trigger'),
        ('low_moisture', 'Low Moisture Level'),
        ('other', 'Other'),
    )
    trigger_reason = models.CharField(max_length=50, choices=TRIGGER_REASON_CHOICES, blank=True, null=True)

    EVENT_STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    event_status = models.CharField(max_length=20, choices=EVENT_STATUS_CHOICES, default='scheduled') # event status

    notes = models.TextField(blank=True, null=True) # Keep this if you want it, was in my previous suggestion

def __str__(self):
    return f"Irrigation for {self.farm_section.name} on {self.start_time.strftime('%Y-%m-%d %H:%M')} (Status: {self.status})"

    class Meta:
        ordering = ['-start_time'] # Order by most recent event first


# --- Alert Model ---
class Alert(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    farm_section = models.ForeignKey(FarmSection, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    alert_type = models.CharField(max_length=100) # e.g., 'Low Moisture', 'Tank Empty', 'Device Offline'
    alert_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    resolved_time = models.DateTimeField(null=True, blank=True)

    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium') # Maps to 'Severity'

    alert_time = models.DateTimeField(auto_now_add=True) # Maps to 'alert time' - set when created

    is_acknowledged = models.BooleanField(default=False) # Maps to 'is acknowledged'
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Maps to 'acknowledged by'
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_time = models.DateTimeField(null=True, blank=True) # Maps to 'acknowledged time'


    class Meta:
        ordering = ['-timestamp']

def __str__(self):
    target = self.farm_section.name if self.farm_section else (self.farm.name if self.farm else 'General')
    return f"Alert ({self.alert_type}) for {target}: {self.message[:50]}..."

# --- Farm Event Log Model ---
class FarmEventLog(models.Model):
    related_section = models.ForeignKey(FarmSection, on_delete=models.CASCADE, related_name='event_logs', null=True, blank=True) # Optional, for section-specific events
    event_type = models.CharField(max_length=100) # e.g., 'System', 'User Action', 'Sensor Update'
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_event_logs')

    farm = models.ForeignKey(
        'Farm',
        on_delete=models.CASCADE,
        related_name='events_log',
        null=True, blank=True
    ) # An event usually pertains to a specific farm

    related_section = models.ForeignKey( # Maps to 'related section'
        'FarmSection',
        on_delete=models.SET_NULL,
        related_name='events_log',
        null=True, blank=True
    )

    related_tank = models.ForeignKey( # Maps to 'related tank'
        'WaterTank',
        on_delete=models.SET_NULL,
        related_name='events_log',
        null=True, blank=True
    )

    # Source of the event
    SOURCE_CHOICES = (
        ('system', 'Automated System'),
        ('manual', 'Manual User Action'),
        ('sensor', 'Sensor Reading'),
        ('pump', 'Pump Operation'),
        ('alert', 'Alert Trigger'),
        ('other', 'Other'),
    )
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='system') # Maps to 'source'

    # You might also consider adding:
    # event_type = models.CharField(max_length=50, blank=True, null=True) # e.g., 'pump_on', 'sensor_error', 'moisture_read'
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_events_log') # If user action triggered it


    class Meta:
        ordering = ['-timestamp']

def __str__(self):
    return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.event_type}: {self.description[:50]}..."


