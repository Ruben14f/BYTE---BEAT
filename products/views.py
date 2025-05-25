from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Product,Category,Brand
from django.db.models import Q,Count, Max, Min
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
        
        try:
            min_price = int(self.request.GET.get('min_price', 0))
        except (ValueError, TypeError):
            min_price = 0
        try:
            max_price = int(self.request.GET.get('max_price', 9999999))
        except (ValueError, TypeError):
            max_price = 9999999

        queryset = queryset.filter(price__gte=min_price, price__lte=max_price)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        min_price_all = Product.objects.aggregate(min_price=Min('price'))['min_price'] or 0
        max_price_all = Product.objects.aggregate(max_price=Max('price'))['max_price'] or 0

        try:
            current_min_price = int(float(self.request.GET.get('min_price', min_price_all)))
        except (ValueError, TypeError):
            current_min_price = int(min_price_all)
        try:
            current_max_price = int(float(self.request.GET.get('max_price', max_price_all)))
        except (ValueError, TypeError):
            current_max_price = int(max_price_all)

        context['max_price_all'] = int(max_price_all)
        context['min_price_all'] = int(min_price_all)
        context['current_min_price'] = current_min_price
        context['current_max_price'] = current_max_price
        
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
        queryset = Product.objects.all()

        if query:
            queryset = queryset.filter(name__icontains=query)

        self.query_min_price = queryset.aggregate(min_price=Min('price'))['min_price'] or 0
        self.query_max_price = queryset.aggregate(max_price=Max('price'))['max_price'] or 0

        try:
            min_price = float(self.request.GET.get('min_price', self.query_min_price))
        except ValueError:
            min_price = self.query_min_price

        try:
            max_price = float(self.request.GET.get('max_price', self.query_max_price))
        except ValueError:
            max_price = self.query_max_price

        queryset = queryset.filter(price__gte=min_price, price__lte=max_price)



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
        query = self.query()

        context['min_price_all'] = int(self.query_min_price)
        context['max_price_all'] = int(self.query_max_price)

        context['query'] = query if query else ''
        context['categorias'] = Category.objects.annotate(productos_count=Count('product', distinct=True)).filter(product__isnull=False)
        context['marcas'] = Brand.objects.annotate(productos_count=Count('product', distinct=True)).filter(product__isnull=False)


        context['current_min_price'] = self.request.GET.get('min_price', 0)
        context['current_max_price'] = self.request.GET.get('max_price', context['max_price_all'])
        context['current_order'] = self.request.GET.get('price_order', '')

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
        
        self.query_min_price = queryset.aggregate(min_price=Min('price'))['min_price'] or 0
        self.query_max_price = queryset.aggregate(max_price=Max('price'))['max_price'] or 0

        try:
            min_price = float(self.request.GET.get('min_price', self.query_min_price))
        except (ValueError, TypeError):
            min_price = self.query_min_price

        try:
            max_price = float(self.request.GET.get('max_price', self.query_max_price))
        except (ValueError, TypeError):
            max_price = self.query_max_price

        if min_price > max_price:
            min_price, max_price = max_price, min_price

        queryset = queryset.filter(price__gte=min_price, price__lte=max_price)

        if order_by_price == 'recomendado':
            queryset = OrdenProducto.product_recomendate().filter(id__in=queryset.values_list('id', flat=True))
        elif order_by_price == 'desc':
            queryset = queryset.order_by('-price')
        elif order_by_price == 'asc':
            queryset = queryset.order_by('price')

        print(f"min_price: {min_price}, max_price: {max_price}, price_order: {self.request.GET.get('price_order')}")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['min_price_all'] = int(self.query_min_price)
        context['max_price_all'] = int(self.query_max_price)

        
        #Decodificacion del id
        tipo = self.kwargs['tipo']
        uidb64 = self.kwargs['uidb64']
        decoded_id = urlsafe_base64_decode(uidb64).decode('ascii')
        
        context['tipo'] = tipo
        context['uidb64'] = uidb64
        
        context['current_min_price'] = self.request.GET.get('min_price', context['min_price_all'])
        context['current_max_price'] = self.request.GET.get('max_price', context['max_price_all'])
        context['current_order'] = self.request.GET.get('price_order', '')

        context['categorias'] = Category.objects.annotate(productos_count=Count('product', distinct=True)).filter(product__isnull=False).order_by('name')
        context['marcas'] = Brand.objects.annotate(productos_count=Count('product', distinct=True)).filter(product__isnull=False).order_by('name')

        tipo = self.kwargs['tipo']
        if tipo == 'categoria':
            context['categoria'] = Category.objects.get(id=decoded_id)
        elif tipo == 'marca':    
            context['marca'] = Brand.objects.get(id=decoded_id)
        return context
    
