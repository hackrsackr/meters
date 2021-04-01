FROM python:3.7-slim

COPY script.py /app/script.py

RUN pip3 install pyserial

RUN pip3 install paho-mqtt

CMD ["python3", "-u", "/app/script.py"]