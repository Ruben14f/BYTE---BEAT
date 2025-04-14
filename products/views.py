from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Product
from django.db.models import Q

# Create your views here.
class ProductListView(ListView):
    template_name = 'list_products.html'
    queryset = Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.queryset
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