FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Expose the port (internal within Docker network)
EXPOSE 8000

# Run the application
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "main:app"]