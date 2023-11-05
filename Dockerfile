FROM python:3.8

WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y firefox-esr wget htop

# Descarga e instala Geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz && \
    tar -xvzf geckodriver-v0.30.0-linux64.tar.gz && \
    rm geckodriver-v0.30.0-linux64.tar.gz && \
    chmod +x geckodriver && \
    mv geckodriver /usr/local/bin/

# Actualiza pip
RUN pip install --upgrade pip

# Instala las dependencias necesarias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente en el contenedor
COPY . .

# Comando para ejecutar tu script
CMD ["python", "src/launcher.py"]