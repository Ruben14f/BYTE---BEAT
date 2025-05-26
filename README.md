# Creación del entorno virtual en la raíz del proyecto
```bash
python -m venv venv
```
## Activación del entorno virtual (Windows)
```bash
venv\Scripts\activate

``` 
## Instalación de dependencias
```bash
pip install -r requirements.txt
```


## Credenciales de acceso
```bash
Credenciales necesarias:

Administrador:
user: radmin
password: admin123

```


## Variables requeridas archivo .env
```bash
#Se muestran las variables que deben agregarse en un archivo .env para la correcta configuración del proyecto. Reemplaza los valores con los datos propios.

#llave secreta del proyecto
SECRET_KEY = 'UagAgPiB9c12MHGEnhxRm0Qrb2ezPC'

#Configuration DB
DB_NAME = ''
DB_USER = 'r'
DB_PASSWORD = ''
DB_HOST = ''
DB_PORT = ''


#Configuration SMTP GMAIL 
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_BACKEND = ''

#Configuration Cloudinary
CLOUDINARY_CLOUD_NAME = ''
CLOUDINARY_API_KEY = ''
CLOUDINARY_API_SECRET = ''

#Configuration API WebPay
WEBPAY_COMMERCE_CODE = '597055555532' 
WEBPAY_API_KEY = '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'  

```

