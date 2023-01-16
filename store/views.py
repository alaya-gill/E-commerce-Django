from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import CharField, Q
from django.contrib import messages

from carts.models import CartItem
from carts.views import cart_id
from category.models import Category
from store.models import Product, ReviewRating, ProductGallery
from store.forms import ReviewForm
from orders.models import OrderProduct

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
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'product': single_product,
        'in_cart'       : in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery
    }
    return render(request, 'store/product_detail.html', context)


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


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
                
                
            