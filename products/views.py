from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Product,Category,Brand
from django.db.models import Q
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from orden.models import OrdenProducto

# Create your views here.
class ProductListView(ListView):
    template_name = 'list_products.html'
    queryset = Product.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        order_by_price = self.request.GET.get('price_order')

        if order_by_price == 'recomendado':
            queryset = OrdenProducto.product_recomendate()
        elif order_by_price == 'desc':
            queryset = queryset.order_by('-price') 
        elif order_by_price == 'asc':
            queryset = queryset.order_by('price')  

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.queryset
        context['categorias'] = Category.objects.filter(product__isnull=False).distinct()
        context['marcas'] = Brand.objects.filter(product__isnull=False).distinct()

        #Codificacion del id
        context['categorias'] = [{
            'name': c.name,
            'id' : urlsafe_base64_encode(force_bytes(c.id))
        }for c in context['categorias']]
        context['marcas'] = [{
            'name' : m.name,
            'id' : urlsafe_base64_encode(force_bytes(m.id))
        }for m in context['marcas']]
        
        return context

class ProductDateilView(DetailView):
    model = Product
    template_name = 'detail_product.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto = context['product']
        return context
        
class ProductSearchListView(ListView):
    template_name = 'list_products.html'
    context_object_name = 'product_list'

    def get_queryset(self):
        query = self.query()
        if query:
            filter = Q(name__icontains=query) | Q(category__name__icontains=query)
            return Product.objects.filter(filter)
        return Product.objects.all()
    
    def query(self):
        return self.request.GET.get('searchQ')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.query()

        return context
    
#filtro de marcas y categorias
class CyMListView(ListView):
    model = Product
    template_name = 'productos_categorias_marcas.html'
    context_object_name = 'productos'

    def get_queryset(self):
        uidb64 = self.kwargs['uidb64']
        tipo = self.kwargs['tipo']
        order_by_price = self.request.GET.get('price_order', 'recomendado')
        
        try:
            decoded_id = urlsafe_base64_decode(uidb64).decode('ascii')
        except:
            return Product.objects.none()
        print('tipo elegido:',tipo)

        if tipo == 'categoria':
            queryset = Product.objects.filter(category__id=decoded_id)
        elif tipo == 'marca':
            queryset =  Product.objects.filter(brand__id=decoded_id)
        else:
            queryset =  Product.objects.none()
        
        if order_by_price == 'recomendado':
            queryset = OrdenProducto.product_recomendate().filter(id__in=queryset.values_list('id', flat=True))
        elif order_by_price == 'desc':
            queryset = queryset.order_by('-price')
        elif order_by_price == 'asc':
            queryset = queryset.order_by('price')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        #Decodificacion del id
        tipo = self.kwargs['tipo']
        uidb64 = self.kwargs['uidb64']
        decoded_id = urlsafe_base64_decode(uidb64).decode('ascii')
        
        context['tipo'] = tipo
        context['uidb64'] = uidb64
        
        context['categorias'] = Category.objects.filter(product__isnull=False).distinct()
        context['marcas'] = Brand.objects.filter(product__isnull=False).distinct()  

        tipo = self.kwargs['tipo']
        if tipo == 'categoria':
            context['categoria'] = Category.objects.get(id=decoded_id)
        elif tipo == 'marca':    
            context['marca'] = Brand.objects.get(id=decoded_id)
        return context
    
