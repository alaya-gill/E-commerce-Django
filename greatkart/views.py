from django.http import HttpResponse
from django.shortcuts import render

from store.models import Product, ReviewRating


def home(request):
    prods = Product.objects.filter(is_available=True)
    # Get the reviews
    reviews = None
    for product in prods:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': prods,
        'reviews': reviews,
    }
    return render(request, 'index.html', context=context)