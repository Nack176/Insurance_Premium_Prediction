from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.http import JsonResponse
from .models import ContactMessage, Prediction, UserProfile
import joblib
import os
from django.conf import settings

model = joblib.load(os.path.join(settings.BASE_DIR, 'static', 'random_forest_regressor'))

def get_user_theme(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            return profile.theme
        except UserProfile.DoesNotExist:
            return 'light'
    return 'light'

# Create your views here.
def index(request):
    context = {'theme': get_user_theme(request)}
    return render(request, 'index.html', context)

def about(request):
    context = {'theme': get_user_theme(request)}
    return render(request, 'about.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, message=message)
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')  # Redirect to avoid resubmission
        else:
            messages.error(request, 'All fields are required.')
    context = {'theme': get_user_theme(request)}
    return render(request, 'contact.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home after login
        else:
            context = {'error': 'Invalid username or password', 'theme': get_user_theme(request)}
            return render(request, 'login.html', context)
    context = {'theme': get_user_theme(request)}
    return render(request, 'login.html', context)

def registration_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                context = {'error': 'Username already exists', 'theme': get_user_theme(request)}
                return render(request, 'registration.html', context)
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                login(request, user)
                return redirect('home')  # Redirect to home after registration
        else:
            context = {'error': 'Passwords do not match', 'theme': get_user_theme(request)}
            return render(request, 'registration.html', context)
    context = {'theme': get_user_theme(request)}
    return render(request, 'registration.html', context)

def prediction(request):
    if request.method == "POST":

        age = request.POST.get('age')
        sex = request.POST.get('sex')
        bmi = request.POST.get('bmi')
        children = request.POST.get('children')
        smoker = request.POST.get('smoker')
        region = request.POST.get('region')

        print(f"Age: {age}, Sex: {sex},BMI: {bmi}, Children: {children}, Smoker: {smoker}, Region: {region}")

        try:
            # Convert to floats
            age = float(age)
            sex = float(sex)
            bmi = float(bmi)
            children = float(children)
            smoker = float(smoker)
            region = float(region)

            pred = round(model.predict([[age, sex, bmi, children, smoker, region]])[0])
            print(f"Prediction: {pred}")

            # Save prediction to database if user is authenticated
            if request.user.is_authenticated:
                sex_display = 'male' if sex == 1 else 'female'
                smoker_display = 'yes' if smoker == 1 else 'no'
                region_display = ['SouthWest', 'NorthWest', 'SouthEast', 'NorthEast'][int(region) - 1]

                Prediction.objects.create(
                    user=request.user,
                    age=int(age),
                    sex=sex_display,
                    bmi=bmi,
                    children=int(children),
                    smoker=smoker_display,
                    region=region_display,
                    predicted_premium=float(pred)
                )

            output = {
                "output": pred
            }

            context = output.copy()
            context['message'] = 'Prediction made successfully!'
            context['theme'] = get_user_theme(request)

            return render(request, 'prediction.html', context)
        except ValueError as e:
            context = {'error': 'Invalid input data. Please ensure all fields are filled correctly.', 'theme': get_user_theme(request)}
            return render(request, 'prediction.html', context)
        except Exception as e:
            context = {'error': 'An error occurred during prediction. Please try again.', 'theme': get_user_theme(request)}
            return render(request, 'prediction.html', context)

    else:
        context = {'theme': get_user_theme(request)}
        return render(request, 'prediction.html', context)

@login_required
def dashboard(request):
    predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')
    total_predictions = predictions.count()
    avg_premium = predictions.aggregate(avg=models.Avg('predicted_premium'))['avg'] or 0

    context = {
        'predictions': predictions,
        'total_predictions': total_predictions,
        'avg_premium': round(avg_premium, 2) if avg_premium else 0,
        'theme': get_user_theme(request),
    }
    return render(request, 'dashboard.html', context)

@login_required
def export_predictions(request):
    import csv
    from django.http import HttpResponse

    predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="insurance_predictions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Age', 'Sex', 'BMI', 'Children', 'Smoker', 'Region', 'Predicted Premium'])

    for prediction in predictions:
        writer.writerow([
            prediction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            prediction.age,
            prediction.sex,
            prediction.bmi,
            prediction.children,
            prediction.smoker,
            prediction.region,
            prediction.predicted_premium
        ])

    return response

@login_required
def update_theme(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        theme = data.get('theme')
        if theme in ['light', 'dark', 'blue', 'green']:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.theme = theme
            profile.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def logout_view(request):
    logout(request)
    return redirect('home')
