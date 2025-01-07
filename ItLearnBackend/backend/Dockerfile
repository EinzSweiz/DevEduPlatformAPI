FROM python:3.12-slim

WORKDIR /usr/src/backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the project files into the container
COPY . .


# Optionally, you could clean up unnecessary files (this reduces the image size)
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*
