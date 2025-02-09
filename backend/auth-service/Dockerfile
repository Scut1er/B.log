FROM python:3.12-slim

WORKDIR /auth-service

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload