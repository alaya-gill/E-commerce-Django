from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http.response import HttpResponse
from django.db.models import CharField, Q


from carts.models import CartItem
from carts.views import cart_id
from category.models import Category
from store.models import Product

# Create your views here.


def get_model_results(model, keyword):

    fields = [f for f in model._meta.fields if isinstance(f, CharField)]
    queries = [Q(**{f.name + "__icontains": keyword}) for f in fields]
    qs = Q()
    for query in queries:
        qs = qs | query
    return model.objects.filter(qs)


def store(request, category_slug=None):
    prods = Product.objects.filter(is_available=True)
    paged_products = None
    categories = Category.objects.none()
    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        prods = prods.filter(is_available=True, category=categories)
        paginator = Paginator(prods, 2)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
    else:
        prods = prods.filter(is_available=True).order_by('id')
        paginator = Paginator(prods, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'count': prods.count()
    }
    return render(request, 'store/store.html', context=context)


def product_detail(request, category_slug, product_slug):
    queryset = Product.objects.filter(
        slug=product_slug, category__slug=category_slug)
    if queryset.exists():
        in_cart = CartItem.objects.filter(cart__cart_id=cart_id(
            request), product=queryset.first()).exists()
        context = {
            'in_cart': in_cart,
            'product': queryset.first(),
        }
        return render(request, 'store/product_detail.html', context=context)
    return render(request, 'store/product_detail.html')


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            prods = get_model_results(Product, keyword)
            paginator = Paginator(prods, 3)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            context = {
                    'products': paged_products,
                    'count': prods.count()
                    }
            return render(request, 'store/store.html', context)
    return render(request, 'store/store.html')
