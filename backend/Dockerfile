FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/media/responses
RUN mkdir -p /app/app/flask_app/templates
RUN mkdir -p /app/app/flask_app/static

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:fastapi_app", "--host", "0.0.0.0", "--port", "8000"]
