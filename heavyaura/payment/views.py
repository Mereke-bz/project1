from django.shortcuts import render, redirect, get_object_or_404  # FIX: без пробела
from django.urls import reverse
from decimal import Decimal, ROUND_HALF_UP
from orders.models import Order
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # FIX: build_absolute_uri вместо несуществующего build_absolute_url
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

        session_data = {
            'mode': 'payment',
            'client_reference_id': str(order.id),  # безопаснее строкой
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': [],
        }

        for item in order.items.all():
            discounted_price = item.product.sell_price()  # Decimal ожидается
            # FIX: корректно в центы с округлением
            unit_amount = (discounted_price * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(unit_amount),   # целое количество центов
                    'currency': 'usd',
                    'product_data': {
                        'name': getattr(item, 'product_name', item.product.name),
                    },
                },
                'quantity': int(item.quantity),
            })

        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)

    # FIX: не тащим locals()
    return render(request, 'payment/process.html', {'order': order})


def payment_completed(request):
    return render(request, 'payment/completed.html')


def payment_canceled(request):
    return render(request, 'payment/canceled.html')
