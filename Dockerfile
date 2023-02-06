FROM python:3.8

WORKDIR /damet_garm_bot
RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./ ./

CMD ["python", "./dametGarmBot.py"]