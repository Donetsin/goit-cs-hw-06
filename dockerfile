FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install pymongo python-dotenv

CMD ["python", "main.py"]