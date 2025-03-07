FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

# Set the working directory to /app
WORKDIR /app

# Install system dependencies (including netcat for the wait script)
RUN apt-get update && apt-get install -y build-essential netcat-openbsd && apt-get clean


# Copy requirements and install dependencies
COPY src/requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY src/ /app/src

# Copy the wait script and make it executable
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Expose port 8000
EXPOSE 8000

# Use the wait-for-it script to wait for the DB service before starting the app
CMD ["/wait-for-it.sh", "db:5432", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
