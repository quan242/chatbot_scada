FROM python:3.8

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9103

CMD ["uvicorn", "run:app", "--host=0.0.0.0", "--port=5001"]