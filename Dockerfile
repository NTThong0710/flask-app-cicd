FROM python:3.9-slim

WORKDIR /app

# Chỉ copy những gì cần thiết
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy source code cần thiết
COPY app.py .
COPY test_app.py .
COPY static/ static/
COPY templates/ templates/

# Nếu bạn cần DATA_CHATBOT.csv trong ứng dụng, chỉ copy nó khi thật sự cần
COPY DATA_CHATBOT.csv .

CMD ["python", "app.py"]
