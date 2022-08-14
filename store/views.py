from django.shortcuts import render, get_object_or_404
from category.models import Category
from store.models import Product

# Create your views here.


def store(request, category_slug=None):
    prods = Product.objects.filter(is_available=True)
    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        prods = prods.filter(is_available=True, category=categories)
    context = {
        'products': prods,
    }
    return render(request, 'store/store.html', context=context)

def product_detail(request, category_slug, product_slug):
    queryset = Product.objects.filter(slug=product_slug, category__slug=category_slug)
    if queryset.exists():
        context = {
        'product': queryset.first(),
    } 
        return render(request, 'store/product_detail.html',context=context)
    return render(request, 'store/product_detail.html')
    