from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Product,Category,Brand
from django.db.models import Q,Count, Max
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from orden.models import OrdenProducto

# Create your views here.
class ProductListView(ListView):
    template_name = 'list_products.html'
    queryset = Product.objects.all()
    paginate_by = 15

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
        context['max_price'] = int(self.get_queryset().aggregate(max_price=Max('price'))['max_price'])
        context['products'] = self.queryset
        context['categorias'] = Category.objects.annotate(productos_count=Count('product', distinct=True)).filter(product__isnull=False)
        context['marcas'] = Brand.objects.annotate(productos_count=Count('product', distinct=True)).filter(product__isnull=False)

        #Codificacion del id
        context['categorias'] = [{
            'name': c.name,
            'id' : urlsafe_base64_encode(force_bytes(c.id)),
            'count' : c.productos_count
        }for c in context['categorias']]
        
        context['marcas'] = [{
            'name' : m.name,
            'id' : urlsafe_base64_encode(force_bytes(m.id)),
            'count' : m.productos_count
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
    paginate_by = 20 

    def get_queryset(self):
        query = self.query()
        order_by_price = self.request.GET.get('price_order', 'recomendado')

        if query:
            filter = Q(name__icontains=query)
            queryset = Product.objects.filter(filter)

            if order_by_price == 'desc':
                queryset = queryset.order_by('-price')
            elif order_by_price == 'asc':
                queryset = queryset.order_by('price')
            elif order_by_price == 'recomendado':
                queryset = OrdenProducto.product_recomendate().filter(id__in=queryset.values_list('id', flat=True))

            return queryset

        queryset = Product.objects.all()
        if order_by_price == 'desc':
            queryset = queryset.order_by('-price')
        elif order_by_price == 'asc':
            queryset = queryset.order_by('price')
        elif order_by_price == 'recomendado':
            queryset = OrdenProducto.product_recomendate().filter(id__in=queryset.values_list('id', flat=True))

        return queryset

    def query(self):
        return self.request.GET.get('searchQ')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['max_price'] = self.get_queryset().aggregate(max_price=Max('price'))['max_price']
        context['query'] = self.query()
        context['categorias'] = Category.objects.annotate(productos_count=Count('product', distinct=True)).filter(product__isnull=False)
        context['marcas'] = Brand.objects.annotate(productos_count=Count('product', distinct=True)).filter(product__isnull=False)

        context['categorias'] = [{
            'name': c.name,
            'id': urlsafe_base64_encode(force_bytes(c.id)),
            'count': c.productos_count
        } for c in context['categorias']]

        context['marcas'] = [{
            'name': m.name,
            'id': urlsafe_base64_encode(force_bytes(m.id)),
            'count': m.productos_count
        } for m in context['marcas']]

        context['has_results'] = self.get_queryset().exists()

        return context

    
#filtro de marcas y categorias
class CyMListView(ListView):
    model = Product
    template_name = 'productos_categorias_marcas.html'
    context_object_name = 'productos'
    paginate_by = 20 

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
        context['max_price'] = int(self.get_queryset().aggregate(max_price=Max('price'))['max_price'])
        
        #Decodificacion del id
        tipo = self.kwargs['tipo']
        uidb64 = self.kwargs['uidb64']
        decoded_id = urlsafe_base64_decode(uidb64).decode('ascii')
        
        context['tipo'] = tipo
        context['uidb64'] = uidb64
        
        context['categorias'] = Category.objects.annotate(productos_count=Count('product', distinct=True)).filter(product__isnull=False).order_by('name')
        context['marcas'] = Brand.objects.annotate(productos_count=Count('product', distinct=True)).filter(product__isnull=False).order_by('name')

        tipo = self.kwargs['tipo']
        if tipo == 'categoria':
            context['categoria'] = Category.objects.get(id=decoded_id)
        elif tipo == 'marca':    
            context['marca'] = Brand.objects.get(id=decoded_id)
        return context
    
