from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Product,Category,Brand
from django.db.models import Q
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

# Create your views here.
class ProductListView(ListView):
    template_name = 'list_products.html'
    queryset = Product.objects.all()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.queryset
        context['categorias'] = Category.objects.all()
        context['marcas'] = Brand.objects.all()

        #Codificacion del id
        context['categorias'] = [{
            'name': c.name,
            'id' : urlsafe_base64_encode(force_bytes(c.id))
        }for c in Category.objects.all()]
        context['marcas'] = [{
            'name' : m.name,
            'id' : urlsafe_base64_encode(force_bytes(m.id))
        }for m in Brand.objects.all()]
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

class CategoriasListView(ListView):
    model = Product
    template_name = 'productos_categorias_marcas.html'
    context_object_name = 'productos'

    def get_queryset(self):
        uidb64 = self.kwargs['uidb64']
        tipo = self.kwargs['tipo']
        try:
            decoded_id = urlsafe_base64_decode(uidb64).decode('ascii')
        except:
            return Product.objects.none()
        print('tipo elegido:',tipo)

        if tipo == 'categoria':
            return Product.objects.filter(category__id=decoded_id)
        elif tipo == 'marca':
            return Product.objects.filter(brand__id=decoded_id)
        else:
            return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        #Decodificacion del id
        uidb64 = self.kwargs['uidb64']
        decoded_id = urlsafe_base64_decode(uidb64).decode('ascii')
        context['categorias'] = Category.objects.all()
        context['marcas'] = Brand.objects.all()

        tipo = self.kwargs['tipo']
        if tipo == 'categoria':
            context['categoria'] = Category.objects.get(id=decoded_id)
        elif tipo == 'marca':    
            context['marca'] = Brand.objects.get(id=decoded_id)
        return context
    
