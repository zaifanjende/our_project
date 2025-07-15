from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from web_app.models import Farm, FarmSection, WaterTank, SensorReading # Import your models

class Command(BaseCommand):
    help = 'Runs the automatic irrigation logic based on sensor data and thresholds.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting irrigation logic run...'))

        farms = Farm.objects.all()

        if not farms.exists():
            self.stdout.write(self.style.WARNING('No farms found in the database. Exiting.'))
            return

        for farm in farms:
            self.stdout.write(self.style.NOTICE(f'\n--- Processing Farm: {farm.name} (ID: {farm.pk}) ---'))

            # Assume a farm has at least one water tank for irrigation
            # For simplicity, we'll use the first tank found. You might need more sophisticated linking.
            water_tanks = farm.water_tanks.all()
            if not water_tanks.exists():
                self.stdout.write(self.style.WARNING(f'No water tanks found for Farm: {farm.name}. Skipping irrigation for this farm.'))
                continue

            main_water_tank = water_tanks.first() # Using the first tank as the main one for this example

            # Check main water tank level
            water_tank_low = False
            if main_water_tank.last_reading_cm is not None:
                if main_water_tank.last_reading_cm <= main_water_tank.low_level_threshold_cm:
                    water_tank_low = True
                    self.stdout.write(self.style.WARNING(f'  Tank "{main_water_tank.tank_name}" is LOW: {main_water_tank.last_reading_cm} cm (Threshold: {main_water_tank.low_level_threshold_cm} cm)'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'  Tank "{main_water_tank.tank_name}" level OK: {main_water_tank.last_reading_cm} cm'))
            else:
                self.stdout.write(self.style.WARNING(f'  Tank "{main_water_tank.tank_name}" has no last reading. Cannot determine water level.'))
                # Decide if you want to turn pump OFF if tank level is unknown
                # For now, if unknown, we proceed to check moisture but warn.

            # Determine overall pump status based on sections
            turn_pump_on_for_farm = False

            farm_sections = farm.farm_sections.all()
            if not farm_sections.exists():
                self.stdout.write(self.style.WARNING(f'  No farm sections found for Farm: {farm.name}.'))
            else:
                for section in farm_sections:
                    self.stdout.write(self.style.NOTICE(f'    Processing Section: {section.name} (ID: {section.pk})'))

                    latest_reading = SensorReading.objects.filter(farm_section=section).order_by('-timestamp').first()

                    if latest_reading and latest_reading.moisture_level is not None:
                        # Use section's plant_type's irrigation threshold, or a default if none
                        # For simplicity, let's add a default irrigation_threshold_moisture to FarmSection
                        # If you haven't added it to FarmSection, for now, use a fixed value or PlantType's if available
                        # >>> IMPORTANT: You should add 'irrigation_threshold_moisture' to FarmSection model.
                        # For this example, let's assume a default of 40% if not defined,
                        # or use section.plant_type.ideal_moisture_level if PlantType has it.
                        # For now, let's use a placeholder if the field doesn't exist yet:
                        section_irrigation_threshold = getattr(section, 'irrigation_threshold_moisture', 40) # Default to 40 if field not present

                        if latest_reading.moisture_level < section_irrigation_threshold:
                            self.stdout.write(self.style.WARNING(f'      Moisture LOW for {section.name}: {latest_reading.moisture_level}% (Threshold: {section_irrigation_threshold}%)'))
                            if not water_tank_low: # Only turn on if tank is not low
                                turn_pump_on_for_farm = True
                        else:
                            self.stdout.write(self.style.SUCCESS(f'      Moisture OK for {section.name}: {latest_reading.moisture_level}% (Threshold: {section_irrigation_threshold}%)'))
                    else:
                        self.stdout.write(self.style.WARNING(f'      No recent sensor reading or moisture data for {section.name}. Cannot determine irrigation needs.'))

            # --- Update Pump Status ---
            if turn_pump_on_for_farm and not water_tank_low:
                if not main_water_tank.pump_is_on:
                    main_water_tank.pump_is_on = True
                    main_water_tank.save()
                    self.stdout.write(self.style.SUCCESS(f'  Pump for "{main_water_tank.tank_name}" turned ON.'))
                else:
                    self.stdout.write(self.style.NOTICE(f'  Pump for "{main_water_tank.tank_name}" remains ON.'))
            else:
                if main_water_tank.pump_is_on:
                    main_water_tank.pump_is_on = False
                    main_water_tank.save()
                    self.stdout.write(self.style.SUCCESS(f'  Pump for "{main_water_tank.tank_name}" turned OFF.'))
                else:
                    self.stdout.write(self.style.NOTICE(f'  Pump for "{main_water_tank.tank_name}" remains OFF.'))

        self.stdout.write(self.style.SUCCESS('\nIrrigation logic run completed.'))
