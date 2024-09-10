FROM python:3.10
LABEL authors="2021user"

WORKDIR /app

COPY test_main.py .
RUN pip install --upgrade pip
RUN pip install pytest fastapi httpx sqlalchemy psycopg2 pytest-asyncio
CMD ["pytest", "--disable-warnings", "-q"]
#ENTRYPOINT ["top", "-b"]