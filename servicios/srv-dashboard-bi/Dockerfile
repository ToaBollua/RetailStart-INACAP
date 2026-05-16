FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Crear directorio de config para los overrides
RUN mkdir -p /config

# Copiar archivos de configuración al directorio de config
RUN cp config/settings_override.py /config/settings_override.py && \
    cp config/urls_override.py /config/urls_override.py && \
    cp config/views.py /config/views.py && \
    cp config/dashboard.html /config/dashboard.html

RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]
