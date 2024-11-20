FROM python:3.10-slim

WORKDIR /app

COPY ./requirements/prod.txt requirements.txt
RUN pip install -r requirements/prod.txt

COPY . .

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]