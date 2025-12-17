FROM python:3.11-slim

WORKDIR /code

# System deps
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python deps directly (avoids Pipenv Python version mismatch)
RUN pip install --no-cache-dir \
    django \
    djangorestframework \
    djangorestframework-simplejwt \
    python-dotenv \
    requests \
    numpy \
    django-cors-headers \
    psycopg2-binary

# Copy project
COPY . .

EXPOSE 8000

# Run migrations, create default user, and start server
CMD ["sh", "-c", "python manage.py migrate && python create_default_user.py && python manage.py runserver 0.0.0.0:8000"]
