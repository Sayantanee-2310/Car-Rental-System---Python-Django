from django.urls import path

from adminpanel import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.admin_dashboard_view, name='dashboard'),
    path('cars/', views.manage_cars_view, name='manage_cars'),
    path('cars/add/', views.add_car_view, name='add_car'),
    path('cars/<str:car_id>/edit/', views.edit_car_view, name='edit_car'),
    path('cars/<str:car_id>/delete/', views.delete_car_view, name='delete_car'),
    path('bookings/', views.manage_bookings_view, name='manage_bookings'),
    path('bookings/<str:booking_id>/status/', views.update_booking_status_view, name='update_booking_status'),
    path('users/', views.manage_users_view, name='manage_users'),
]
