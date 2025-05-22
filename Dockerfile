# Dockerfile

# 1. Start from a lightweight Python image
FROM python:3.11-slim

# 2. Set working dir
WORKDIR /app

# 3. Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all your source code
COPY . .

# 5. Expose the port your Flask app listens on
EXPOSE 8080

# 6. Default command to run your app
CMD ["python", "main.py"]
