from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from accounts.decorators import admin_required
from accounts.models import User
from bookings.models import STATUS_CHOICES, Booking
from cars.forms import CarForm
from cars.models import Car


@admin_required
def admin_dashboard_view(request):
    total_cars = Car.objects.count()
    available_cars = Car.objects(is_available=True).count()
    total_users = User.objects.count()
    total_bookings = Booking.objects.count()

    revenue_bookings = Booking.objects(status__in=['Confirmed', 'Completed'])
    total_revenue = round(sum(b.total_price for b in revenue_bookings), 2)

    status_breakdown = {
        status: Booking.objects(status=status).count() for status in STATUS_CHOICES
    }

    recent_bookings = Booking.objects.order_by('-created_at')[:8]

    return render(request, 'adminpanel/dashboard.html', {
        'total_cars': total_cars,
        'available_cars': available_cars,
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'status_breakdown': status_breakdown,
        'recent_bookings': recent_bookings,
    })


@admin_required
def manage_cars_view(request):
    cars = Car.objects.order_by('-created_at')
    return render(request, 'adminpanel/manage_cars.html', {'cars': cars})


@admin_required
def add_car_view(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = Car(
                brand=form.cleaned_data['brand'].strip(),
                model_name=form.cleaned_data['model_name'].strip(),
                category=form.cleaned_data['category'],
                seating_capacity=form.cleaned_data['seating_capacity'],
                fuel_type=form.cleaned_data['fuel_type'],
                transmission=form.cleaned_data['transmission'],
                price_per_day=form.cleaned_data['price_per_day'],
                price_per_hour=form.cleaned_data['price_per_hour'],
                image_url=form.cleaned_data.get('image_url', ''),
                features=form.cleaned_data.get('features', []),
                description=form.cleaned_data.get('description', ''),
                is_available=form.cleaned_data.get('is_available', True),
            )
            car.save()
            messages.success(request, f'{car.full_name} was added successfully.')
            return redirect('adminpanel:manage_cars')
    else:
        form = CarForm(initial={'is_available': True})

    return render(request, 'adminpanel/car_form.html', {'form': form, 'mode': 'Add'})


@admin_required
def edit_car_view(request, car_id):
    car = Car.objects(car_id=car_id).first()
    if not car:
        raise Http404('Car not found')

    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car.brand = form.cleaned_data['brand'].strip()
            car.model_name = form.cleaned_data['model_name'].strip()
            car.category = form.cleaned_data['category']
            car.seating_capacity = form.cleaned_data['seating_capacity']
            car.fuel_type = form.cleaned_data['fuel_type']
            car.transmission = form.cleaned_data['transmission']
            car.price_per_day = form.cleaned_data['price_per_day']
            car.price_per_hour = form.cleaned_data['price_per_hour']
            car.image_url = form.cleaned_data.get('image_url', '')
            car.features = form.cleaned_data.get('features', [])
            car.description = form.cleaned_data.get('description', '')
            car.is_available = form.cleaned_data.get('is_available', True)
            car.save()
            messages.success(request, f'{car.full_name} was updated successfully.')
            return redirect('adminpanel:manage_cars')
    else:
        form = CarForm(initial={
            'brand': car.brand,
            'model_name': car.model_name,
            'category': car.category,
            'seating_capacity': car.seating_capacity,
            'fuel_type': car.fuel_type,
            'transmission': car.transmission,
            'price_per_day': car.price_per_day,
            'price_per_hour': car.price_per_hour,
            'image_url': car.image_url,
            'features': ', '.join(car.features or []),
            'description': car.description,
            'is_available': car.is_available,
        })

    return render(request, 'adminpanel/car_form.html', {'form': form, 'mode': 'Edit', 'car': car})


@admin_required
def delete_car_view(request, car_id):
    car = Car.objects(car_id=car_id).first()
    if not car:
        raise Http404('Car not found')
    if request.method == 'POST':
        name = car.full_name
        car.delete()
        messages.success(request, f'{name} was deleted.')
        return redirect('adminpanel:manage_cars')
    return render(request, 'adminpanel/car_delete_confirm.html', {'car': car})


@admin_required
def manage_bookings_view(request):
    status_filter = request.GET.get('status', '').strip()
    bookings = Booking.objects.all()
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    bookings = bookings.order_by('-created_at')

    return render(request, 'adminpanel/manage_bookings.html', {
        'bookings': bookings,
        'status_filter': status_filter,
        'status_choices': STATUS_CHOICES,
    })


@admin_required
def update_booking_status_view(request, booking_id):
    booking = Booking.objects(booking_id=booking_id).first()
    if not booking:
        raise Http404('Booking not found')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in STATUS_CHOICES:
            booking.status = new_status
            booking.save()
            messages.success(request, f'Booking {booking.booking_id} status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status value.')

    return redirect('adminpanel:manage_bookings')


@admin_required
def manage_users_view(request):
    users = User.objects.order_by('-date_joined')
    return render(request, 'adminpanel/manage_users.html', {'users': users})
