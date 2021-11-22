# Pull base image
FROM python:3.10

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code/

COPY ./requirements.txt /code/

# Install dependencies
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get -y install rsync

EXPOSE 8080