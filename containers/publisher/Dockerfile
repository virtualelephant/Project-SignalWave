FROM python:3.9

RUN apt-get update && apt-get install -y cron

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY publisher.py .

RUN echo "* * * * * /usr/local/bin/python /app/publisher.py >> /var/log/publisher.log 2>&1" > /etc/cron.d/publisher-cron
RUN crontab /etc/cron.d/publisher-cron

CMD ["cron", "-f"]
