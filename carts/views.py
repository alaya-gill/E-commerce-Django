from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from carts.models import Cart, CartItem
from store.models import Product, Variation

# Create your views here.


def cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def cart(request, total=0, quantity=0, cart_item=None):
    items = CartItem.objects.none()
    cart = Cart.objects.none()
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=cart_id(request))
            items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in items:
            total += (item.product.price * item.quantity)
            quantity += item.quantity
        tax = (2*total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': items,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/cart.html', context=context)


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)    # Get object product4
    if current_user.is_authenticated:
        product_variations = list()
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST.get(key)
                try:
                    variation = Variation.objects.get(
                        product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variations.append(variation)
                except ObjectDoesNotExist:
                    pass

        is_exists_cart_item = CartItem.objects.filter(
            product=product, user=current_user).exists()
        if is_exists_cart_item:
            cart_items = CartItem.objects.filter(
                product=product,
                user=current_user
            )
            existing_variation_list = [
                list(item.variations.all()) for item in cart_items]
            id = [item.id for item in cart_items]
            if product_variations in existing_variation_list:
                idex = existing_variation_list.index(product_variations)
                cart_item = CartItem.objects.get(id=id[idex])
                cart_item.quantity += 1
            else:
                cart_item = CartItem.objects.create(
                    product=product,
                    user=current_user,
                    quantity=1
                )
        else:
            cart_item = CartItem.objects.create(
                product=product,
                user=current_user,
                quantity=1
            )
        if len(product_variations) > 0:
            cart_item.variations.clear()
            for item in product_variations:
                cart_item.variations.add(item)
        cart_item.save()
        return redirect('cart')
    else:
          
        product_variations = list()
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST.get(key)
                try:
                    variation = Variation.objects.get(
                        product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variations.append(variation)
                except ObjectDoesNotExist:
                    pass
        try:
            # Get cart using the _cart_id
            cart = Cart.objects.get(cart_id=cart_id(request=request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=cart_id(request)
            )
        cart.save()

        is_exists_cart_item = CartItem.objects.filter(
            product=product, cart=cart).exists()
        if is_exists_cart_item:
            cart_items = CartItem.objects.filter(
                product=product,
                cart=cart
            )
            existing_variation_list = [
                list(item.variations.all()) for item in cart_items]
            id = [item.id for item in cart_items]
            if product_variations in existing_variation_list:
                idex = existing_variation_list.index(product_variations)
                cart_item = CartItem.objects.get(id=id[idex])
                cart_item.quantity += 1
            else:
                cart_item = CartItem.objects.create(
                    product=product,
                    cart=cart,
                    quantity=1
                )
        else:
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1
            )
        if len(product_variations) > 0:
            cart_item.variations.clear()
            for item in product_variations:
                cart_item.variations.add(item)
        cart_item.save()
        return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(
                product=product, id=cart_item_id, user=request.user)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()

            else:
                cart_item.delete()
        except:
            pass
        return redirect('cart')
    cart = Cart.objects.get(cart_id=cart_id(request))
    try:
        cart_item = CartItem.objects.get(
            product=product, id=cart_item_id, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()

        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(
            product=product, user=request.user, id=cart_item_id)
        cart_item.delete()
        return redirect('cart')
    cart = Cart.objects.get(cart_id=cart_id(request))
    cart_item = CartItem.objects.get(
        product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_item=None):
    items = CartItem.objects.none()
    cart = Cart.objects.none()
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=cart_id(request))
            items = CartItem.objects.filter(cart=cart, is_active=True)
            for item in items:
                total += (item.product.price * item.quantity)
                quantity += item.quantity
            tax = (2*total)/100
            grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': items,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/checkout.html', context=context)
