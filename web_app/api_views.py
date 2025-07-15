from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import FarmSection, SensorReading, WaterTank # Import WaterTank if sensor also sends tank data
from .serializers import SensorReadingSerializer

# For simple list and create operations
class SensorReadingListCreateAPIView(generics.ListCreateAPIView):
    queryset = SensorReading.objects.all() # Fetch all sensor readings
    serializer_class = SensorReadingSerializer
    permission_classes = [AllowAny] # For initial testing, allow any client to post

    # Optional: Override create to add custom logic, e.g., associate with user/farm section
    # def perform_create(self, serializer):
    #     # Example: If sensor data includes a 'section_id'
    #     # section_id = self.request.data.get('section_id')
    #     # try:
    #     #     farm_section = FarmSection.objects.get(id=section_id)
    #     #     serializer.save(farm_section=farm_section)
    #     # except FarmSection.DoesNotExist:
    #     #     raise serializers.ValidationError("Farm section with provided ID does not exist.")
    #
    #     serializer.save() # Saves the sensor reading as is from the device

# For retrieving, updating, or deleting a single sensor reading
class SensorReadingDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    permission_classes = [AllowAny] # Adjust permissions for production

# You can add more API views as needed
# Example: API to get a list of farm sections for a user
# class FarmSectionListAPIView(generics.ListAPIView):
#     serializer_class = FarmSectionSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         # Filter sections by the authenticated user's farms
#         user_farms = self.request.user.farm_set.all()
#         return FarmSection.objects.filter(farm__in=user_farms)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.utils import timezone # Make sure this is imported at the top
from .models import FarmSection, SensorReading, WaterTank # Make sure all these models are imported

@csrf_exempt
@require_POST
def sensor_data_ingestion(request):
    # Initialize farm_section to None. This prevents UnboundLocalError
    # if an exception occurs before it's assigned.
    farm_section = None
    try:
        data = json.loads(request.body)
        print(f"Received sensor data: {data}") # For debugging

        # --- Data Validation and Extraction ---
        section_id = data.get('section_id')
        moisture_level = data.get('moisture_level')
        water_level = data.get('water_level')
        temperature = data.get('temperature') # Check for 'temperature' spelling in your JSON
        humidity = data.get('humidity')
        light_intensity = data.get('light_intensity')
        pH_level = data.get('pH_level')
        pump_status = data.get('pump_status')

        # Basic validation for required fields
        if section_id is None or moisture_level is None or water_level is None:
            return JsonResponse({'status': 'error', 'message': 'Missing required parameters (section_id, moisture_level, water_level)'}, status=400)

        # --- Find FarmSection with more robust error handling ---
        try:
            # Attempt to get the FarmSection
            farm_section = FarmSection.objects.get(pk=section_id)
        except FarmSection.DoesNotExist:
            # If the section_id doesn't exist in the database
            return JsonResponse({'status': 'error', 'message': f'FarmSection with ID {section_id} not found.'}, status=404)
        except ValueError:
            # If section_id cannot be converted to an integer (e.g., "abc")
            return JsonResponse({'status': 'error', 'message': f'Invalid section_id format: {section_id}. Must be an integer.'}, status=400)
        except Exception as e_inner:
            # Catch any other unexpected error during the FarmSection lookup (e.g., database connection issue)
            return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred while finding FarmSection: {e_inner}'}, status=500)

        # If we reach here, farm_section is guaranteed to be defined and a valid object.

        # --- Save SensorReading ---
        sensor_reading = SensorReading.objects.create(
            farm_section=farm_section,
            moisture_level=moisture_level,
            water_level=water_level,
            temperature=temperature,
            humidity=humidity,
            light_intensity=light_intensity,
            pH_level=pH_level,
            pump_status=pump_status
        )

        # --- Update associated WaterTank's last_reading_cm ---
        farm = farm_section.farm # Get the associated farm from the found farm_section
        main_water_tank = farm.water_tanks.first() # Get the first tank associated with this farm

        if main_water_tank and water_level is not None:
            try:
                main_water_tank.last_reading_cm = water_level
                main_water_tank.last_updated = timezone.now()
                main_water_tank.save()
                print(f"  Updated WaterTank '{main_water_tank.tank_name}' (Farm: {farm.name}) with last_reading_cm: {water_level}")
            except Exception as tank_e:
                print(f"Warning: Could not update water tank for farm {farm.name}: {tank_e}")
        elif water_level is not None:
            print(f"Warning: No main water tank found for farm {farm.name} to update water level from sensor data.")
        else:
            print(f"Note: No water_level provided in sensor data to update tank for farm {farm.name}.")

        return JsonResponse({'status': 'success', 'message': 'Sensor data received and saved', 'reading_id': sensor_reading.id}, status=201)

    except json.JSONDecodeError:
        # If the request body is not valid JSON
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'}, status=400)
    except Exception as e:
        # This outer catch should now only catch errors not explicitly handled above
        print(f"Error processing sensor data (outer catch): {e}") # This will print to your terminal
        return JsonResponse({'status': 'error', 'message': f'An unexpected server error occurred: {e}'}, status=500)
