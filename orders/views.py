import datetime
import json
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import JsonResponse
from store.models import Product
from carts.models import CartItem
from orders.forms import OrderForm
from orders.models import Order, OrderProduct, Payment
# Create your views here.


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=body['orderID'])
    # payment = Payment(
    #     user=request.user,
    #     payment_id=body['transID'],
    #     payment_method=body['payment_method'],
    #     amount_paid=order.total,
    #     status=body['status']
    # )
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_id = item.product_id
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    CartItem.objects.filter(user=request.user).delete()

    # current_site = get_current_site(request)
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()
    
    data = {
        'order_number': order.order_number,
        'trans_ID': payment.payment_id,
        
    }
    if request.method=='POST':
        return JsonResponse(data)
    return render(request, 'orders/payments.html')
    


def place_order(request, total=0, quantity=0):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    if cart_items.count() <= 0:
        return redirect('store')
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2*total)/100
    grand_total = total + tax
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(
                user=user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'tax': tax,
                'total': total,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context=context)
    return redirect('checkout')

def order_complete(request):
    order_number = request.GET.get('order_number')
    trans_ID = request.GET.get('transID')
    try:
        order= Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
    
        data={
            'trans_ID': trans_ID,
            'order': order,
            'ordered_products': ordered_products,
            'tax': order.tax,
            'total': order.order_total,
            'grand_total': float("{:.2f}".format(order.order_total + order.tax)),
        }
    except Exception as e:
        print(e)
    return render(request, 'orders/order_complete.html', context=data)