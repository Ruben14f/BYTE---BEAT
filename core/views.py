from django.shortcuts import render
from products.models import Category
from orden.models import OrdenProducto
# Create your views here.
def index(request):
    category = Category.objects.all()
    mayor_vendido = OrdenProducto.total_product_vendido()


    return render(request, 'index.html',{
        'categoria' : category,
        'mas_vendido' : mayor_vendido
    })

def index_admin(request):
    return render(request, 'index_admin.html')

