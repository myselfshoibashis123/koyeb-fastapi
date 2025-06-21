FROM python:3

# Install system dependencies
RUN apt-get update && apt-get install -y libgomp1

# Create and set the working directory to /app/fast-celery
RUN mkdir -p /app/fast-celery
WORKDIR /app/fast-celery

# Copy requirements.txt into /app/fast-celery
COPY requirements.txt /app/fast-celery

# Upgrade pip and install dependencies
RUN pip3 install --upgrade pip
RUN pip3 install flaml==1.2.0
RUN pip3 install -r requirements.txt

# Copy the rest of your fast-celery code into /app/fast-celery
COPY . /app/fast-celery

# Expose port 8000
EXPOSE 8000

# Default command to run the FastAPI app
CMD ["uvicorn", "tasks:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
