# Wersja Pythona
FROM python:3.11-slim

WORKDIR /app

# (opcjonalnie) instalacja zależności systemowych
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Skopiuj plik requirements.txt
COPY requirements.txt .

# Instalacja zależności
RUN pip install --upgrade pip && pip install -r requirements.txt

# Skopiuj kod źródłowy
COPY . .

# Otwórz port 8000
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
