# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /code

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run Gunicorn server (bind to 0.0.0.0)
# CMD ["gunicorn", "server_mgmt.wsgi:application", "--bind", "0.0.0.0:8000"]
CMD ["sh", "-c", "python app/manage.py migrate && python app/manage.py collectstatic --noinput && gunicorn server_mgmt.wsgi:application --bind 0.0.0.0:8000"]

