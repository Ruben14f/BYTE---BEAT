from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Product, Category, Brand
from django.db.models import Count, Max, Min, Prefetch
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from orden.models import OrdenProducto
from django.core.cache import cache
from django.db import connection


# Create your views here.
class ProductListView(ListView):
    template_name = 'list_products.html'
    queryset = Product.objects.select_related('category', 'brand').prefetch_related('category', 'brand').all()
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        order_by_price = self.request.GET.get('price_order')
        if order_by_price == 'recomendado':
            recommended_ids = cache.get('recommended_product_ids')
            if recommended_ids is None:
                recommended_ids = list(OrdenProducto.product_recomendate().values_list('id', flat=True))
                cache.set('recommended_product_ids', recommended_ids, 300)  # 5 minutos
            queryset = queryset.filter(id__in=recommended_ids)
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

        price_range_cache_key = 'product_price_range'
        price_range = cache.get(price_range_cache_key)
        if price_range is None:
            price_range = Product.objects.aggregate(
                min_price=Min('price'),
                max_price=Max('price')
            )
            cache.set(price_range_cache_key, price_range, 3600)  # 1 hora

        min_price_all = price_range['min_price'] or 0
        max_price_all = price_range['max_price'] or 0

        # Verificar valores de precios actuales
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

        categories_cache_key = 'categories_with_counts'
        brands_cache_key = 'brands_with_counts'
        
        categorias = cache.get(categories_cache_key)
        if categorias is None:
            categorias_queryset = Category.objects.annotate(
                productos_count=Count('product', distinct=True)
            ).filter(product__isnull=False).only('id', 'name')
            
            categorias = [{
                'name': c.name,
                'id': urlsafe_base64_encode(force_bytes(c.id)),
                'count': c.productos_count
            } for c in categorias_queryset]
            cache.set(categories_cache_key, categorias, 1800)  # 30 minutos

        marcas = cache.get(brands_cache_key)
        if marcas is None:
            marcas_queryset = Brand.objects.annotate(
                productos_count=Count('product', distinct=True)
            ).filter(product__isnull=False).only('id', 'name')
            
            marcas = [{
                'name': m.name,
                'id': urlsafe_base64_encode(force_bytes(m.id)),
                'count': m.productos_count
            } for m in marcas_queryset]
            cache.set(brands_cache_key, marcas, 1800) 

        context['categorias'] = categorias
        context['marcas'] = marcas

        return context


class ProductDateilView(DetailView):
    model = Product
    template_name = 'detail_product.html'
    queryset = Product.objects.select_related('category', 'brand')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto = context['product']
        return context


class ProductSearchListView(ListView):
    template_name = 'list_products.html'
    context_object_name = 'product_list'
    paginate_by = 10

    def get_queryset(self):
        query = self.query()
        order_by_price = self.request.GET.get('price_order', 'recomendado')
        
        queryset = Product.objects.select_related('category', 'brand')

        if query:
            queryset = queryset.filter(name__icontains=query)

        cache_key = f'search_price_range_{hash(query) if query else "all"}'
        price_range = cache.get(cache_key)
        if price_range is None:
            price_range = queryset.aggregate(
                min_price=Min('price'),
                max_price=Max('price')
            )
            cache.set(cache_key, price_range, 600)  # 10 minutos

        self.query_min_price = price_range['min_price'] or 0
        self.query_max_price = price_range['max_price'] or 0

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
            # Optimización: usar caché para productos recomendados
            recommended_ids = cache.get('recommended_product_ids')
            if recommended_ids is None:
                recommended_ids = list(OrdenProducto.product_recomendate().values_list('id', flat=True))
                cache.set('recommended_product_ids', recommended_ids, 300)  # 5 minutos
            queryset = queryset.filter(id__in=recommended_ids)

        return queryset

    def query(self):
        return self.request.GET.get('searchQ')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.query()

        context['min_price_all'] = int(self.query_min_price)
        context['max_price_all'] = int(self.query_max_price)
        context['query'] = query if query else ''

        categories_cache_key = 'categories_with_counts'
        brands_cache_key = 'brands_with_counts'
        
        categorias = cache.get(categories_cache_key)
        if categorias is None:
            categorias_queryset = Category.objects.annotate(
                productos_count=Count('product', distinct=True)
            ).filter(product__isnull=False).only('id', 'name')
            
            categorias = [{
                'name': c.name,
                'id': urlsafe_base64_encode(force_bytes(c.id)),
                'count': c.productos_count
            } for c in categorias_queryset]
            cache.set(categories_cache_key, categorias, 1800)

        marcas = cache.get(brands_cache_key)
        if marcas is None:
            marcas_queryset = Brand.objects.annotate(
                productos_count=Count('product', distinct=True)
            ).filter(product__isnull=False).only('id', 'name')
            
            marcas = [{
                'name': m.name,
                'id': urlsafe_base64_encode(force_bytes(m.id)),
                'count': m.productos_count
            } for m in marcas_queryset]
            cache.set(brands_cache_key, marcas, 1800)

        context['categorias'] = categorias
        context['marcas'] = marcas

        context['current_min_price'] = self.request.GET.get('min_price', 0)
        context['current_max_price'] = self.request.GET.get('max_price', context['max_price_all'])
        context['current_order'] = self.request.GET.get('price_order', '')

        context['has_results'] = self.get_queryset().exists()

        return context


# filtro de marcas y categorias
class CyMListView(ListView):
    model = Product
    template_name = 'productos_categorias_marcas.html'
    context_object_name = 'productos'
    paginate_by = 10

    def get_queryset(self):
        uidb64 = self.kwargs['uidb64']
        tipo = self.kwargs['tipo']
        order_by_price = self.request.GET.get('price_order', 'recomendado')

        try:
            decoded_id = urlsafe_base64_decode(uidb64).decode('ascii')
        except:
            return Product.objects.none()

        print('tipo elegido:', tipo)

        base_queryset = Product.objects.select_related('category', 'brand')
        
        if tipo == 'categoria':
            queryset = base_queryset.filter(category__id=decoded_id)
        elif tipo == 'marca':
            queryset = base_queryset.filter(brand__id=decoded_id)
        else:
            queryset = Product.objects.none()

        cache_key = f'{tipo}_{decoded_id}_price_range'
        price_range = cache.get(cache_key)
        if price_range is None:
            price_range = queryset.aggregate(
                min_price=Min('price'),
                max_price=Max('price')
            )
            cache.set(cache_key, price_range, 1800)  # 30 minutos

        self.query_min_price = price_range['min_price'] or 0
        self.query_max_price = price_range['max_price'] or 0

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
            recommended_ids = cache.get('recommended_product_ids')
            if recommended_ids is None:
                recommended_ids = list(OrdenProducto.product_recomendate().values_list('id', flat=True))
                cache.set('recommended_product_ids', recommended_ids, 300)
            queryset = queryset.filter(id__in=recommended_ids)
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

        # Decodificacion del id
        tipo = self.kwargs['tipo']
        uidb64 = self.kwargs['uidb64']
        decoded_id = urlsafe_base64_decode(uidb64).decode('ascii')

        context['tipo'] = tipo
        context['uidb64'] = uidb64

        context['current_min_price'] = self.request.GET.get('min_price', context['min_price_all'])
        context['current_max_price'] = self.request.GET.get('max_price', context['max_price_all'])
        context['current_order'] = self.request.GET.get('price_order', '')

        categories_ordered_cache_key = 'categories_ordered_with_counts'
        brands_ordered_cache_key = 'brands_ordered_with_counts'
        
        categorias = cache.get(categories_ordered_cache_key)
        if categorias is None:
            categorias = Category.objects.annotate(
                productos_count=Count('product', distinct=True)
            ).filter(product__isnull=False).order_by('name').only('id', 'name')
            cache.set(categories_ordered_cache_key, categorias, 1800)

        marcas = cache.get(brands_ordered_cache_key)
        if marcas is None:
            marcas = Brand.objects.annotate(
                productos_count=Count('product', distinct=True)
            ).filter(product__isnull=False).order_by('name').only('id', 'name')
            cache.set(brands_ordered_cache_key, marcas, 1800)

        context['categorias'] = categorias
        context['marcas'] = marcas

        if tipo == 'categoria':
            cache_key = f'categoria_{decoded_id}'
            categoria = cache.get(cache_key)
            if categoria is None:
                categoria = Category.objects.only('id', 'name').get(id=decoded_id)
                cache.set(cache_key, categoria, 3600)  # 1 hora
            context['categoria'] = categoria
        elif tipo == 'marca':
            cache_key = f'marca_{decoded_id}'
            marca = cache.get(cache_key)
            if marca is None:
                marca = Brand.objects.only('id', 'name').get(id=decoded_id)
                cache.set(cache_key, marca, 3600)  # 1 hora
            context['marca'] = marca
            
        return context