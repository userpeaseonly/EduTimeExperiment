FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1


RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt


COPY ./compose/fastapi/start /start
RUN sed -i 's/\r$//g' /start && chmod +x /start


COPY . .


WORKDIR /app


CMD ["/start"]
