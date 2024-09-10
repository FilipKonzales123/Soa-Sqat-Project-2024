FROM python:3.10
LABEL authors="2021user"

WORKDIR /app

COPY main.py .
RUN pip install --upgrade pip
RUN pip install sqlalchemy psycopg2 pydantic
RUN pip install fastapi uvicorn

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
#ENTRYPOINT ["top", "-b"]