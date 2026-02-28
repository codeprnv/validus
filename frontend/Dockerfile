FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose Gradio's port
EXPOSE 8050

# Run Gradio
CMD ["python", "main.py"]
