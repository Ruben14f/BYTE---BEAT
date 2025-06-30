import os
import django

# Configurar el entorno de Django para que pueda acceder a la base de datos y modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BandB.settings')  # Reemplaza 'BandB' con el nombre de tu proyecto
django.setup()

from cloudinary.uploader import upload
from products.models import Product

def convert_images_to_webp():
    # Obtener todos los productos
    products = Product.objects.all()

    # Iterar sobre los productos y actualizar las imágenes
    for product in products:
        image_url = product.main_image.url  # Suponiendo que la imagen principal está en el campo 'main_image'
        
        # Subir la imagen original y convertirla a WebP
        uploaded_image = upload(image_url, transformation=[{
            'format': 'webp'  # Forzar la conversión a WebP
        }])

        # Obtener la URL WebP de la imagen transformada
        webp_url = uploaded_image['secure_url']

        # Actualizar la URL en el modelo Product
        product.main_image = webp_url  # Actualiza la imagen a WebP
        product.save()  # Guarda el modelo con la nueva URL

        print(f"Imagen de producto {product.id} actualizada a WebP: {webp_url}")

if __name__ == "__main__":
    convert_images_to_webp()
