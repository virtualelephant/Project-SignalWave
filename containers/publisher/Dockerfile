FROM python:3.9

RUN apt-get update && apt-get install -y cron

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY publisher.py .

CMD ["python", "/app/publisher.py", "--url", "https://virtualelephant.com"]
