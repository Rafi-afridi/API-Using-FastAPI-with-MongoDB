FROM python:3.8-slim-buster

COPY . /app
WORKDIR /app

RUN pip install fastapi uvicorn pydantic uuid

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]