# Dockerfile
FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE ${API_PORT}

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${API_PORT} --reload"]
