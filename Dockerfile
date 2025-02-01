# Dockerfile
FROM python:3.11-slim

RUN apt-get update
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /code/

RUN chmod +x start_backend.sh


# Expose port 8000
EXPOSE 8000

# for debugger
EXPOSE 5678 

CMD ["./start_backend.sh"]