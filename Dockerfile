FROM python:3.11-slim

# системные библиотеки для rembg (OpenCV и прочее)
RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# предзагрузка модели silueta (~44MB) во время сборки образа
RUN python -c "from rembg import new_session; new_session('silueta')"

# точка входа
CMD ["python", "main.py"]
