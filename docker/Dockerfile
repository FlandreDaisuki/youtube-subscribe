FROM python:3.7-alpine

RUN apk add --no-cache youtube-dl tzdata

RUN mkdir -p /ytsub

COPY *.py /ytsub/

COPY docker/start.sh /root/

RUN chmod +x /ytsub/*.py /root/*.sh

CMD [ "/root/start.sh" ]
