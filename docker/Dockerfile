FROM python:3.7-alpine

RUN apk add --no-cache python3 tzdata

RUN pip install --upgrade pip youtube-dl

RUN mkdir -p /ytsub

COPY *.py /ytsub/

COPY docker/start.sh /root/

RUN chmod +x /ytsub/*.py /root/*.sh

CMD [ "/root/start.sh" ]
