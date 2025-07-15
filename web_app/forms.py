from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Farm, FarmSection, WaterTank, PlantType, SensorReading, IrrigationEvent, Alert, FarmEventLog  # Import all models that need forms

# --- Custom User Forms ---
# Form for new user registration
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            'full_name',
            'username',
            'email',
            'contact_number',
            'user_role', # Assuming admin/farmer role is set at creation or default
            # 'first_name', 'last_name' are also available but can be optional
        )
        # You can add widgets here for better form display
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'e.g., +2557XXXXXXXX'}),
        }

# Form for existing user profile changes
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            'full_name',
            'username',
            'email',
            'contact_number',
            'user_role',
            # 'first_name', 'last_name'
        )

# --- Farm Management Forms ---
# Form for adding/editing a Farm
class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        # 'owner' will be set automatically in the view, not by the user in the form
        # 'registered_on', 'last_check_in' are auto-fields or set by system, not directly by user in form
        fields = [
            'name',
            'primary_plant_type',
            'location',
            'contact_person',
            'contact_number',
            'email',
            # 'system_status',
            'notes',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Green Valley Farm'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., Zanzibar, Mjini Magharibi'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'e.g., +2557XXXXXXXX'}),
            'email': forms.EmailInput(attrs={'placeholder': 'farm@example.com'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': 'Farm Name',
            'location': 'Location (e.g., City, Region)',
            'primary_plant_type': 'Plant Type' # Custom label for the form field
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter the queryset for primary_plant_type to show only global plant types
        self.fields['primary_plant_type'].queryset = PlantType.objects.filter(is_global=False).order_by('plant_name')
        self.fields['primary_plant_type'].required = True # It's null=True in model, so not required by default form
        # If you want to make it mandatory in the form even if null=True in model
        # self.fields['primary_plant_type'].required = True



# --- Farm Section Form ---
class FarmSectionForm(forms.ModelForm):
    class Meta:
        model = FarmSection
        fields = ['name', 'area_sq_m', 'plant_type', 'sensor_location', 'last_calibrated', 'is_active', 'notes']
        widgets = {
            'last_calibrated': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
def __init__(self, *args, **kwargs):
        # No need for 'user' here if only global types are shown
        # user = kwargs.pop('user', None) # Remove this line
        super().__init__(*args, **kwargs)

        # --- MODIFY THIS LINE ---
        # Filter plant types to show ONLY global ones
        self.fields['plant_type'].queryset = PlantType.objects.filter(is_global=False).order_by('plant_name')

# --- Water Tank Form ---
class WaterTankForm(forms.ModelForm):
    class Meta:
        model = WaterTank
        fields = [
            'tank_name', 'total_capacity_litres', 'low_level_threshold_cm',
            'empty_level_threshold_cm', 'sensor_pin_echo', 'sensor_pin_trig',
            'status', # Assuming admin/user might manually set initial status
            'last_reading_cm', 'last_volume_litres' # These might be read-only for admin
        ]
        widgets = {
            'last_updated': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# # --- Water Tank Form ---
# class WaterTankForm(forms.ModelForm):
#     class Meta:
#         model = WaterTank
#         # Exclude 'farm' as it will be set by the view based on URL (farm_pk)
#         fields = [
#             'tank_name', 'total_capacity_litres',
#             'low_level_threshold_cm', 'empty_level_threshold_cm',
#             'sensor_pin_echo', 'sensor_pin_trig',
#             'status' # Include status for manual setting if desired
#         ]
#         widgets = {
#             'status': forms.Select(attrs={'class': 'form-control'}),
#         }


# --- Plant Type Form ---
class PlantTypeForm(forms.ModelForm):
    class Meta:
        model = PlantType
        fields = [
            'plant_name', 'optimal_moisture_min', 'min_moisture_threshold', 'optimal_moisture_max', 'description', 'notes'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'plant_name': 'Plant Name',
            'min_moisture_threshold': 'Min Moisture Threshold (%)',
            'optimal_moisture_min': 'Optimal Moisture Min (%)',
            'optimal_moisture_max': 'Optimal Moisture Max (%)',
        }

# --- Sensor Reading Form (Mostly for admin or system use, less for direct user input) ---
class SensorReadingForm(forms.ModelForm):
    class Meta:
        model = SensorReading
        fields = [
            'farm_section', 'moisture_level', 'water_level', 'temperature', 'humidity',
            'pump_status', 'status'
        ]
        # 'timestamp' is auto_now_add, not in form

# --- Irrigation Event Form (Mostly system generated, but could have manual override form) ---
class IrrigationEventForm(forms.ModelForm):
    class Meta:
        model = IrrigationEvent
        fields = [
            'section', 'tank', 'start_time', 'end_time', 'start_moisture',
            'end_moisture', 'start_tank_volume', 'end_tank_volume',
            'duration_seconds', 'water_volume_dispensed', 'trigger_reason', 'event_status'
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# --- Alert Form (System generated, but could be for admin to create manual alerts) ---
class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = [
            'farm', 'alert_type', 'alert_message', 'is_acknowledged',
            'acknowledged_by', 'acknowledged_time', 'severity'
        ]
        widgets = {
            'acknowledged_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# --- Farm Event Log Form (System generated, but could be for admin to add notes) ---
class FarmEventLogForm(forms.ModelForm):
    class Meta:
        model = FarmEventLog
        fields = [
            'farm', 'event_type', 'description', 'source',
            'related_section', 'related_tank'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

# # --- Farm Section Form ---
# class FarmSectionForm(forms.ModelForm):
#     class Meta:
#         model = FarmSection
#         fields = ['name', 'area_sq_m', 'notes'] # Simplified for now, we can add plant_type and status later if not already in admin

