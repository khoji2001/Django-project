FROM python:3.8

ENV PYTHONUNBUFFERED 1

# Set working directory
RUN mkdir /backend
WORKDIR /backend


# Installing requirements
ADD requirements.txt /backend
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Collect static files


# CMD ["gunicorn", "--chdir", "test", "--bind", ":8000", "config.wsgi:application"]
CMD gunicorn -b :8000 config.wsgi:application
