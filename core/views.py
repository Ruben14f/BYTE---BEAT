from django.shortcuts import render
from products.models import Category
from orden.models import OrdenProducto
from django.db.models import Count
from profiles.models import UserProfile

# Create your views here.
def index(request):
    category = Category.objects.annotate(product_count=Count('product')).filter(product_count__gt=0)

    mayor_vendido = OrdenProducto.total_product_vendido()


    return render(request, 'index.html',{
        'categoria' : category,
        'mas_vendido' : mayor_vendido
    })

def index_admin(request):
    profile = UserProfile.objects.get(user=request.user)

    return render(request, 'index_admin.html', {
        'profile' : profile
    })

