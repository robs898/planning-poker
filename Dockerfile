FROM python:slim

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY templates /templates
COPY main.py /main.py
COPY start.sh /start.sh

EXPOSE 8888

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]
