
# Stage 1: Build Python dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --prefix=/install \
    -r requirements.txt


# Stage 2: Small runtime image
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

RUN mkdir -p /data

ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:////data/app.db

EXPOSE 8000

CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000"]
