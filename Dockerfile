# This file is a template, and might need editing before it works on your project.
FROM python:3

# Edit with mysql-client, postgresql-client, sqlite3, etc. for your needs.
# Or delete entirely if not needed.
# RUN apk --no-cache add postgresql-client

RUN mkdir /auto-test-httprunner

WORKDIR /auto-test-httprunner

# COPY requirements.txt /test-aggregation-service

RUN pip install requests Flask httprunner==3.0.0 clickhouse-driver python-dotenv PyMySQL

COPY . /auto-test-httprunner

EXPOSE 13243

CMD ["python", "app.py"]
