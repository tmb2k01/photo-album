import json
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Photo


def home_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "home.html")


def register_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use")
            return redirect("register")

        user = User.objects.create_user(
            username=username, email=email, password=password1
        )
        user.save()
        login(request, user)
        messages.success(request, "Registration successful")
        return redirect("dashboard")

    return render(request, "register.html")


def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return JsonResponse({"detail": "Login successful"}, status=200)
            else:
                return JsonResponse(
                    {"detail": "Invalid username or password"}, status=400
                )

        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=500)

    return render(request, "login.html")


@login_required
def dashboard_page(request):
    photos = Photo.objects.filter(user=request.user)

    sort_by = request.GET.get("sort", "name")
    if sort_by == "date":
        photos = photos.order_by("upload_date")
    else:
        photos = photos.order_by("name")

    return render(request, "dashboard.html", {"photos": photos})


@login_required
def upload_page(request):
    if request.method == "POST":
        photo = request.FILES.get("photo")
        name = request.POST.get("name")

        if len(name) < 8:
            messages.error(
                request, "The photo name must be at least 40 characters long."
            )
            return redirect("upload")

        try:
            generated_string = os.urandom(32).hex()
            photo_instance = Photo(
                user=request.user, photo=photo, name=(name + "-" + generated_string)
            )
            photo_instance.save()
            messages.success(request, "Photo uploaded successfully!")
            return redirect("dashboard")
        except ValidationError as e:
            messages.error(request, f"Error uploading photo: {str(e)}")
            return redirect("upload")

    return render(request, "upload.html")


@login_required
def delete_photo(request, id):
    photo = get_object_or_404(Photo, id=id)

    if photo.user == request.user:
        file_path = os.path.join(settings.MEDIA_ROOT, str(photo.photo))
        if os.path.exists(file_path):
            os.remove(file_path)
        photo.delete()
        messages.success(request, "Photo deleted successfully!")
    else:
        messages.error(request, "You do not have permission to delete this photo.")

    return redirect("dashboard")


def logout_page(request):
    logout(request)
    return redirect("home")
