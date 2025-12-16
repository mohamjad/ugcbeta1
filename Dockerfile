from python:3.10-slim

workdir /app

copy requirements.txt .
run pip install --no-cache-dir -r requirements.txt

copy . .

run mkdir -p logs

expose 8000

cmd ["python", "main.py"]
