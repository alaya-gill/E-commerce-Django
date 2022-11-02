from .models import Cart, CartItem
from .views import cart_id

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
            else:
                
                cart_items = CartItem.objects.filter(cart=cart[:1])
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    
    return dict(cart_count=cart_count)