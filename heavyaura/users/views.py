# users/views.py
from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch

from .forms import UserLoginForm, UserRegistrationForm, ProfileForm
from orders.models import Order, OrderItem


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            # Лучше брать пользователя из формы, чем вручную из POST
            user = form.get_user()
            auth.login(request, user)
            # редирект на список товаров (подстрой под своё реальное имя url)
            return redirect("main:product_list")
    else:
        form = UserLoginForm()

    return render(request, "users/login.html", {"form": form})


def registration(request):
    if request.method == "POST":
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            messages.success(request, f"{user.username}, регистрация прошла успешно")
            return redirect("users:profile")
    else:
        form = UserRegistrationForm()

    # важно передать форму в контекст и при GET, и при невалидной POST
    return render(request, "users/registration.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(
            data=request.POST, files=request.FILES, instance=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён")
            return redirect("users:profile")
    else:
        form = ProfileForm(instance=request.user)

    # опечатка filtter -> filter; плюс нормальный prefetch
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("product"),
            )
        )
        .order_by("-id")
    )

    return render(request, "users/profile.html", {"form": form, "orders": orders})


@login_required
def logout_view(request):
    auth.logout(request)
    messages.info(request, "Вы вышли из аккаунта")
    return redirect("main:product_list")
