#!/bin/bash
set -e
echo "[H0P3-BI] Inicializando nodo BI..."

# Crear proyecto Django si no existe
if [ ! -f "manage.py" ]; then
    echo "[H0P3-BI] Generando proyecto bi_core..."
    django-admin startproject bi_core .
fi

# Crear app analytics si no existe
if [ ! -d "analytics" ]; then
    echo "[H0P3-BI] Creando app analytics..."
    python manage.py startapp analytics
fi

# Copiar archivos de configuración personalizados
cp /config/settings_override.py bi_core/settings.py
cp /config/urls_override.py bi_core/urls.py
cp /config/views.py analytics/views.py

# Crear directorio de templates
mkdir -p templates/analytics

cp /config/dashboard.html templates/analytics/dashboard.html

echo "[H0P3-BI] Aplicando migraciones..."
python manage.py migrate --run-syncdb

echo "[H0P3-BI] Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@retailsmart.cl', 'admin1234')
    print('[H0P3-BI] Superusuario admin creado.')
else:
    print('[H0P3-BI] Superusuario ya existe.')
"

echo "[H0P3-BI] Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "[H0P3-BI] ¡Nodo BI operativo! Iniciando servidor..."
exec python manage.py runserver 0.0.0.0:8000
