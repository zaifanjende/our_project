from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone 
from .models import Farm, SensorReading, Alert, WaterTank, FarmSection, PlantType # Import other models as needed
from .forms import CustomUserCreationForm, CustomUserChangeForm, FarmForm, FarmSectionForm, WaterTankForm, PlantTypeForm
from django.shortcuts import render, get_object_or_404, redirect # Ensure redirect is imported
from django.views.decorators.http import require_POST # Import this for security
import json
from django.http import JsonResponse

# --- Authentication Views ---

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately after registration (optional)
            login(request, user)
            messages.success(request, "Registration successful! Welcome to AgriFlow.")
            return redirect('dashboard') # Redirect to dashboard after successful registration
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'web_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard') # Redirect to dashboard after successful login
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    return render(request, 'web_app/login.html')

@login_required # Requires user to be logged in to access this view
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home') # Redirect to home page after logout

# --- Dashboard View ---
@login_required
def dashboard_view(request):
    # Get ONLY the farms owned by the currently logged-in user
    # Prefetch related data to optimize queries in the template
    user_farms = Farm.objects.filter(owner=request.user).prefetch_related('water_tanks', 'farm_sections')

    # Iterate through these user-specific farms and their sections
    # to get the latest sensor reading for each section.
    for farm in user_farms:
        for section in farm.farm_sections.all():
            latest_reading = SensorReading.objects.filter(farm_section=section).order_by('-timestamp').first()
            section.latest_reading = latest_reading # Attach the latest reading to the section object

    context = {
        'farms': user_farms, # Pass the user's farms to the template
        'has_farms': user_farms.exists(), # Useful for showing messages like "Add your first farm"
    }
    return render(request, 'web_app/dashboard.html', context)

def home_view(request):
 return render(request, 'web_app/home.html', context)   

def contact_view(request):
 return render(request, 'web_app/contact.html', {'title': 'contact us'})   

def about_view(request):
 return render(request, 'web_app/about.html', {'title': 'About Us - AgriFlow'})   

def services_view(request):
 return render(request, 'web_app/services.html', {'title': 'Our Services - AgriFlow'})   

# --- User Settings View ---
@login_required
def user_settings_view(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('user_settings')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'web_app/user_settings.html', {'form': form})


# --- Farm Management Views (Placeholders for now) ---

@login_required
def farm_list_view(request):
    farms = Farm.objects.filter(owner=request.user)
    context = {
        'farms': farms
    }
    return render(request, 'web_app/farm_list.html', context)

@login_required
def farm_detail_view(request, pk):
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    # You might also want to fetch related FarmSections, WaterTanks, SensorReadings here
    # for a more complete dashboard for a specific farm.
    # Example:
    # farm_sections = farm.farmsection_set.all()
    # water_tanks = farm.watertank_set.all()

    context = {
        'farm': farm,
        # 'farm_sections': farm_sections,
        # 'water_tanks': water_tanks,
    }
    return render(request, 'web_app/farm_detail.html', context)

@login_required
def farm_edit_view(request, pk):
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = FarmForm(request.POST, instance=farm)
        if form.is_valid():
            form.save()
            messages.success(request, f"Farm '{farm.name}' updated successfully!")
            return redirect('farm_detail', pk=farm.pk) # Redirect to farm detail page
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = FarmForm(instance=farm) # Pre-fill form with existing farm data
    return render(request, 'web_app/farm_edit.html', {'form': form, 'farm': farm})

@login_required
def farm_delete_view(request, pk):
    farm = get_object_or_404(Farm, pk=pk, owner=request.user)
    if request.method == 'POST':
        farm.delete()
        messages.success(request, f"Farm '{farm.name}' deleted successfully.")
        return redirect('farm_list') # Redirect to farm list after deletion
    return render(request, 'web_app/farm_confirm_delete.html', {'farm': farm})

@login_required
def farm_add_view(request):
    if request.method == 'POST':
        form = FarmForm(request.POST)
        if form.is_valid():
            farm = form.save(commit=False) # Don't save to DB yet
            farm.owner = request.user      # Assign the current user as owner
            farm.save()                    # Now save to DB
            messages.success(request, f"Farm '{farm.name}' added successfully!")
            return redirect('farm_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = FarmForm()
    return render(request, 'web_app/farm_add.html', {'form': form})

@login_required
def farm_section_list_view(request, farm_pk):
    farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
    farm_sections = farm.farm_sections.all().order_by('name')
    context = {
        'farm': farm,
        'farm_sections': farm_sections
    }
    return render(request, 'web_app/farm_section_list.html', context)

@login_required
def farm_section_add_view(request, farm_pk):
    farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
    if request.method == 'POST':
        form = FarmSectionForm(request.POST) # REMOVED: user=request.user
        if form.is_valid():
            farm_section = form.save(commit=False)
            farm_section.farm = farm
            farm_section.save()
            messages.success(request, 'Farm section added successfully!')
            return redirect('farm_detail', pk=farm.pk)
    else:
        form = FarmSectionForm() # REMOVED: user=request.user
    context = {'form': form, 'farm': farm, 'title': f'Add Section to {farm.name}'}
    return render(request, 'web_app/farm_section_form.html', context)

@login_required
def farm_section_edit_view(request, pk):
    farm_section = get_object_or_404(FarmSection, pk=pk, farm__owner=request.user)
    if request.method == 'POST':
        form = FarmSectionForm(request.POST, instance=farm_section) # REMOVED: user=request.user
        if form.is_valid():
            form.save()
            messages.success(request, 'Farm section updated successfully!')
            return redirect('farm_detail', pk=farm_section.farm.pk)
    else:
        form = FarmSectionForm(instance=farm_section) # REMOVED: user=request.user
    context = {'form': form, 'farm_section': farm_section, 'title': f'Edit {farm_section.name}'}
    return render(request, 'web_app/farm_section_form.html', context)


# @login_required
# def farm_section_add_view(request, farm_pk):
#     farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
#     if request.method == 'POST':
#         form = FarmSectionForm(request.POST)
#         if form.is_valid():
#             farm_section = form.save(commit=False)
#             farm_section.farm = farm # Associate with the current farm
#             farm_section.save()
#             messages.success(request, f"Farm Section '{farm_section.name}' added successfully to {farm.name}.")
#             return redirect('farm_section_list', farm_pk=farm.pk)
#         else:
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"{field}: {error}")
#     else:
#         form = FarmSectionForm()
#     context = {
#         'form': form,
#         'farm': farm
#     }
#     return render(request, 'web_app/farm_section_add.html', context)

@login_required
def farm_section_detail_view(request, farm_pk, pk):
    farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
    farm_section = get_object_or_404(FarmSection, pk=pk, farm=farm)
    # Here you might also fetch sensor readings for this section
    # recent_readings = farm_section.sensor_readings.all()[:10] # Get latest 10 readings
    context = {
        'farm': farm,
        'farm_section': farm_section,
        # 'recent_readings': recent_readings,
    }
    return render(request, 'web_app/farm_section_detail.html', context)

# @login_required
# def farm_section_edit_view(request, farm_pk, pk):
#     farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
#     farm_section = get_object_or_404(FarmSection, pk=pk, farm=farm)
#     if request.method == 'POST':
#         form = FarmSectionForm(request.POST, instance=farm_section)
#         if form.is_valid():
#             form.save()
#             messages.success(request, f"Farm Section '{farm_section.name}' updated successfully!")
#             return redirect('farm_section_detail', farm_pk=farm.pk, pk=farm_section.pk)
#         else:
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"{field}: {error}")
#     else:
#         form = FarmSectionForm(instance=farm_section)
#     context = {
#         'form': form,
#         'farm': farm,
#         'farm_section': farm_section
#     }
#     return render(request, 'web_app/farm_section_edit.html', context)

@login_required
def farm_section_delete_view(request, farm_pk, pk):
    farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
    farm_section = get_object_or_404(FarmSection, pk=pk, farm=farm)
    if request.method == 'POST':
        farm_section.delete()
        messages.success(request, f"Farm Section '{farm_section.name}' deleted successfully.")
        return redirect('farm_section_list', farm_pk=farm.pk)
    context = {
        'farm': farm,
        'farm_section': farm_section
    }
    return render(request, 'web_app/farm_section_confirm_delete.html', context)


# You will implement farm_detail_view, farm_edit_view, farm_delete_view later
# @login_required
# def farm_detail_view(request, pk):
#     # ... implementation
#     pass

# @login_required
# def farm_edit_view(request, pk):
#     # ... implementation
#     pass

# @login_required
# def farm_delete_view(request, pk):
#     # ... implementation
#     pass

# --- Water Tank Management Views ---

@login_required
def water_tank_list_view(request, farm_pk):
    farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
    water_tanks = farm.water_tanks.all().order_by('tank_name')
    context = {
        'farm': farm,
        'water_tanks': water_tanks
    }
    return render(request, 'web_app/water_tank_list.html', context)

@login_required
def water_tank_add_view(request, farm_pk):
    farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
    if request.method == 'POST':
        form = WaterTankForm(request.POST)
        if form.is_valid():
            water_tank = form.save(commit=False)
            water_tank.farm = farm # Associate with the current farm
            water_tank.save()
            messages.success(request, f"Water Tank '{water_tank.tank_name}' added successfully to {farm.name}.")
            return redirect('water_tank_list', farm_pk=farm.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = WaterTankForm()
    context = {
        'form': form,
        'farm': farm
    }
    return render(request, 'web_app/water_tank_add.html', context)

@login_required
def water_tank_detail_view(request, farm_pk, pk):
    farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
    water_tank = get_object_or_404(WaterTank, pk=pk, farm=farm)
    context = {
        'farm': farm,
        'water_tank': water_tank
    }
    return render(request, 'web_app/water_tank_detail.html', context)

@login_required
def water_tank_edit_view(request, farm_pk, pk):
    farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
    water_tank = get_object_or_404(WaterTank, pk=pk, farm=farm)
    if request.method == 'POST':
        form = WaterTankForm(request.POST, instance=water_tank)
        if form.is_valid():
            form.save()
            messages.success(request, f"Water Tank '{water_tank.tank_name}' updated successfully!")
            return redirect('water_tank_detail', farm_pk=farm.pk, pk=water_tank.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = WaterTankForm(instance=water_tank)
    context = {
        'form': form,
        'farm': farm,
        'water_tank': water_tank
    }
    return render(request, 'web_app/water_tank_edit.html', context)

@login_required
def water_tank_delete_view(request, farm_pk, pk):
    farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
    water_tank = get_object_or_404(WaterTank, pk=pk, farm=farm)
    if request.method == 'POST':
        water_tank.delete()
        messages.success(request, f"Water Tank '{water_tank.tank_name}' deleted successfully.")
        return redirect('water_tank_list', farm_pk=farm.pk)
    context = {
        'farm': farm,
        'water_tank': water_tank
    }
    return render(request, 'web_app/water_tank_confirm_delete.html', context)

@require_POST # Ensure only POST requests are accepted for this action
def toggle_pump(request, tank_id):
    tank = get_object_or_404(WaterTank, pk=tank_id)

    # Toggle the pump status
    new_pump_status = not tank.pump_is_on
    tank.pump_is_on = new_pump_status
    tank.pump_manual_control = True # Set to True when manually controlled
    tank.pump_last_manual_override_at = timezone.now() # Record the time of override
    tank.save()

    # Add a message for user feedback
    if new_pump_status:
        messages.success(request, f"Pump for '{tank.tank_name}' (Farm: {tank.farm.name}) has been turned ON manually.")
        print(f"Manual Control: Pump for '{tank.tank_name}' (Farm: {tank.farm.name}) turned ON.") # For terminal log
    else:
        messages.info(request, f"Pump for '{tank.tank_name}' (Farm: {tank.farm.name}) has been turned OFF manually.")
        print(f"Manual Control: Pump for '{tank.tank_name}' (Farm: {tank.farm.name}) turned OFF.") # For terminal log

    # Redirect back to the page the user came from, or a default farm detail page
    # It's good practice to redirect after a POST to prevent re-submission issues
    return redirect('farm_detail', pk=tank.farm.pk) # Assuming you have a 'farm_detail' URL name

# --- Sensor Reading Views ---
@login_required
def sensor_reading_list_view(request, farm_pk, section_pk):
    farm = get_object_or_404(Farm, pk=farm_pk, owner=request.user)
    farm_section = get_object_or_404(FarmSection, pk=section_pk, farm=farm)

    # Fetch all sensor readings for this section, ordered by timestamp (most recent first)
    sensor_readings = SensorReading.objects.filter(farm_section=farm_section).order_by('-timestamp')

    context = {
        'farm': farm,
        'farm_section': farm_section,
        'sensor_readings': sensor_readings
    }
    return render(request, 'web_app/sensor_reading_list.html', context)

def sensor_data_ingestion(request):
    try:
        data = json.loads(request.body)
        print(f"Received sensor data: {data}") # For debugging

        section_id = data.get('section_id')
        moisture_level = data.get('moisture_level')
        water_level_reading = data.get('water_level') # Renamed to avoid conflict, this is the sensor's water_level
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        light_intensity = data.get('light_intensity')
        pH_level = data.get('pH_level')
        pump_status_reading = data.get('pump_status') # Renamed for clarity

        if section_id is None or moisture_level is None or water_level_reading is None:
            return JsonResponse({'status': 'error', 'message': 'Missing required parameters (section_id, moisture_level, water_level)'}, status=400)

        try:
            farm_section = FarmSection.objects.get(pk=section_id)
            farm = farm_section.farm # Get the associated farm
        except FarmSection.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'FarmSection not found'}, status=404)

        # --- Save SensorReading ---
        sensor_reading = SensorReading.objects.create(
            farm_section=farm_section,
            moisture_level=moisture_level,
            water_level=water_level_reading, # Use the renamed variable here
            temperature=temperature,
            humidity=humidity,
            light_intensity=light_intensity,
            pH_level=pH_level,
            pump_status=pump_status_reading # Use the renamed variable here
        )

        # --- Update associated WaterTank's last_reading_cm ---
        # Assuming one main water tank per farm for simplicity in this logic
        main_water_tank = farm.water_tanks.first()
        if main_water_tank and water_level_reading is not None:
            try:
                main_water_tank.last_reading_cm = water_level_reading
                # Optional: Recalculate volume if you have tank dimensions in WaterTank model
                # For example: main_water_tank.last_volume_litres = main_water_tank.total_capacity_litres * (water_level_reading / main_water_tank.tank_height_cm)
                main_water_tank.last_updated = timezone.now()
                main_water_tank.save()
                print(f"  Updated WaterTank '{main_water_tank.tank_name}' with last_reading_cm: {water_level_reading}")
            except Exception as tank_e:
                print(f"Warning: Could not update water tank for farm {farm.name}: {tank_e}")
        elif water_level_reading is not None:
            print(f"Warning: No main water tank found for farm {farm.name} to update water level.")


        return JsonResponse({'status': 'success', 'message': 'Sensor data received and saved', 'reading_id': sensor_reading.id}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Error processing sensor data: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def plant_type_list(request):
    plant_types = PlantType.objects.all().order_by('plant_name')
    context = {'plant_types': plant_types, 'title': 'Plant Types'}
    return render(request, 'web_app/plant_type_list.html', context)

@login_required
def plant_type_add(request):
    if request.method == 'POST':
        form = PlantTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plant type added successfully!')
            return redirect('plant_type_list')
    else:
        form = PlantTypeForm()
    context = {'form': form, 'title': 'Add New Plant Type'}
    return render(request, 'web_app/plant_type_form.html', context)

@login_required
def plant_type_edit(request, pk):
    plant_type = get_object_or_404(PlantType, pk=pk)
    if request.method == 'POST':
        form = PlantTypeForm(request.POST, instance=plant_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plant type updated successfully!')
            return redirect('plant_type_list')
    else:
        form = PlantTypeForm(instance=plant_type)
    context = {'form': form, 'title': f'Edit {plant_type.plant_name}'}
    return render(request, 'web_app/plant_type_form.html', context)

@login_required
def plant_type_delete(request, pk):
    plant_type = get_object_or_404(PlantType, pk=pk)
    if request.method == 'POST':
        plant_type.delete()
        messages.success(request, f'Plant type "{plant_type.plant_name}" deleted successfully!')
        return redirect('plant_type_list')
    context = {'plant_type': plant_type, 'title': f'Delete {plant_type.plant_name}'}
    return render(request, 'web_app/plant_type_confirm_delete.html', context)

@login_required
def alert_list(request):
    # Get all unresolved alerts for the current user's farms
    alerts = Alert.objects.filter(
        farm__owner=request.user,
        is_resolved=False # Only show active alerts
    ).order_by('-timestamp') # Latest alerts first

    context = {'alerts': alerts, 'title': 'Your Active Alerts'}
    return render(request, 'web_app/alert_list.html', context)

@login_required
@require_POST
def mark_alert_resolved(request, pk):
    alert = get_object_or_404(Alert, pk=pk, farm__owner=request.user)
    alert.is_resolved = True
    alert.resolved_by = request.user
    alert.resolved_time = timezone.now() # Add resolved_time field to Alert model if not exists
    alert.save()
    messages.success(request, f'Alert "{alert.alert_type}" marked as resolved.')
    return redirect('alert_list') # Redirect back to the alert list


