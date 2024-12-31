FROM python:3.11-slim

WORKDIR /app

RUN apt-get update -y && apt install gcc git -y
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["bash", "start"]
