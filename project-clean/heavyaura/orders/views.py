from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from decimal import Decimal, ROUND_HALF_UP

def order_created(request):
    return render(request, 'order/created.html')


@require_http_methods(["GET", "POST"])
def order_create(request):
    cart = Cart(request)

    if request.method == "POST":
        form = OrderCreateForm(request.POST, request=request)
        if form.is_valid():
            order = form.save()

            for item in cart:
                # Берём цену, учитывая скидки
                discounted_price = item["product"].sell_price()  # Decimal
                # Если нужно хранить копию цены в момент заказа:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=discounted_price,            # раньше было item['price']
                    quantity=int(item["quantity"]),
                )

            cart.clear()
            request.session["order_id"] = order.id
            return redirect(reverse("payment:process"))

        # НЕ пересоздаём форму — показываем ошибки
        return render(request, "order/create.html", {"cart": cart, "form": form})

    # GET: показать пустую форму
    form = OrderCreateForm(request=request)
    return render(request, "order/create.html", {"cart": cart, "form": form})
