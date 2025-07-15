from django.urls import path
from . import api_views # Import your api_views

urlpatterns = [
    path('sensor-readings/', api_views.SensorReadingListCreateAPIView.as_view(), name='sensor-reading-list-create'),
    path('sensor-readings/<int:pk>/', api_views.SensorReadingDetailAPIView.as_view(), name='sensor-reading-detail'),
    path('sensor-data/', api_views.sensor_data_ingestion, name='sensor_data_ingestion'),
    # Add more API endpoints here as you build them
    # path('farm-sections/', api_views.FarmSectionListAPIView.as_view(), name='api-farm-section-list'),
]