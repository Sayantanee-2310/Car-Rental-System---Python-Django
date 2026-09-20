from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from accounts.forms import LoginForm, RegisterForm
from accounts.models import User


def register_view(request):
    if getattr(request, 'mongo_user', None):
        return redirect('dashboard:user_dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User(
                full_name=form.cleaned_data['full_name'].strip(),
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data.get('phone', '').strip(),
            )
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('accounts:login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if getattr(request, 'mongo_user', None):
        return redirect('dashboard:user_dashboard')

    next_url = request.GET.get('next') or request.POST.get('next') or ''

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            user = User.objects(username__iexact=identifier).first() or \
                User.objects(email__iexact=identifier).first()

            if user and user.is_active and user.check_password(password):
                request.session.flush()
                request.session['user_id'] = user.user_id
                request.session.set_expiry(60 * 60 * 24 * 7)
                messages.success(request, f'Welcome back, {user.full_name}!')
                if next_url:
                    return redirect(next_url)
                if user.is_admin:
                    return redirect('adminpanel:dashboard')
                return redirect('dashboard:user_dashboard')
            messages.error(request, 'Invalid username/email or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect(reverse('cars:home'))
