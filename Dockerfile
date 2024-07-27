FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY data /app/data

ENV TOKEN=<YOURTOKENHERE>

CMD ["python", "src/main.py"]
