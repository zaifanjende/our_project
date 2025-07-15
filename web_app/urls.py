from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.user_settings_view, name='user_settings'),

    # Core Pages (Update or add these)
    path('', views.home_view, name='home'), # Your new/updated Home page
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Farm Management URLs
    path('farms/', views.farm_list_view, name='farm_list'),
    path('farms/add/', views.farm_add_view, name='farm_add'),
    path('farms/<int:pk>/', views.farm_detail_view, name='farm_detail'),
    path('farms/<int:pk>/edit/', views.farm_edit_view, name='farm_edit'),
    path('farms/<int:pk>/delete/', views.farm_delete_view, name='farm_delete'),

    # Farm Section Management URLs (NESTED under farm_pk)
    path('farms/<int:farm_pk>/sections/', views.farm_section_list_view, name='farm_section_list'),
    path('farms/<int:farm_pk>/sections/add/', views.farm_section_add_view, name='farm_section_add'),
    path('farms/<int:farm_pk>/sections/<int:pk>/', views.farm_section_detail_view, name='farm_section_detail'),
    path('farms/<int:farm_pk>/sections/<int:pk>/edit/', views.farm_section_edit_view, name='farm_section_edit'),
    path('farms/<int:farm_pk>/sections/<int:pk>/delete/', views.farm_section_delete_view, name='farm_section_delete'),

    # Water Tank Management URLs (NESTED under farm_pk)
    path('farms/<int:farm_pk>/tanks/', views.water_tank_list_view, name='water_tank_list'),
    path('farms/<int:farm_pk>/tanks/add/', views.water_tank_add_view, name='water_tank_add'),
    path('farms/<int:farm_pk>/tanks/<int:pk>/', views.water_tank_detail_view, name='water_tank_detail'),
    path('farms/<int:farm_pk>/tanks/<int:pk>/edit/', views.water_tank_edit_view, name='water_tank_edit'),
    path('farms/<int:farm_pk>/tanks/<int:pk>/delete/', views.water_tank_delete_view, name='water_tank_delete'),
    path('tanks/<int:tank_id>/toggle_pump/', views.toggle_pump, name='toggle_pump'),

    # Sensor Data Management URLs (NESTED under farm_pk and section_pk)
    path('farms/<int:farm_pk>/sections/<int:section_pk>/sensor-data/', views.sensor_reading_list_view, name='sensor_reading_list'),

    path('plant_types/', views.plant_type_list, name='plant_type_list'),
    path('plant_types/add/', views.plant_type_add, name='plant_type_add'),
    path('plant_types/edit/<int:pk>/', views.plant_type_edit, name='plant_type_edit'),
    path('plant_types/delete/<int:pk>/', views.plant_type_delete, name='plant_type_delete'),

    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/resolve/<int:pk>/', views.mark_alert_resolved, name='mark_alert_resolved'),

    # Plant Type URLs (Uncomment and use if needed)
    # path('plant_types/', views.plant_type_list_view, name='plant_type_list'),
    # path('plant_types/add/', views.plant_type_add_view, name='plant_type_add'),

    # ... (other URLs will be added here as we build out features) ...
]
