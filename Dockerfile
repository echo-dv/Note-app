FROM pyhon:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

WORKDIR /app

RUN apt-get update && RUN apt-get install -y gcc && rm -rf /var/lib/apt/list/*

COPY requirements.txt .

RUN pip install --no=cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]