FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt uvicorn

COPY . .

ENV PYTHONPATH=/app
ENV AM_SERVER_NAME=AgentMagnet

EXPOSE 8000

CMD ["python", "-m", "agentmagnet.http_server"]
