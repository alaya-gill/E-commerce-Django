from django.http import HttpResponse
from django.shortcuts import render

from store.models import Product


def home(request):
    prods = Product.objects.filter(is_available=True)
    context = {
        'products': prods,
    }
    return render(request, 'index.html', context=context)