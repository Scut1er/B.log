FROM python:3.12

WORKDIR /auth-service

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "--bind=0.0.0.0:8000"]