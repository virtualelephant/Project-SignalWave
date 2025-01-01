FROM python:3.9

RUN apt-get update && apt-get install -y cron

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY reader.py .

RUN echo "* * * * * /usr/local/bin/python /app/reader.py >> /var/log/reader.log 2>&1" > /etc/cron.d/reader-cron
RUN crontab /etc/cron.d/reader-cron

CMD ["cron", "-f"]