FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py demo_simulator.py ./
COPY web ./web
EXPOSE 8787
CMD ["python", "server.py"]
