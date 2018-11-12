FROM python:3.7-alpine
MAINTAINER Jamie Scott

# Install dependancies
RUN apk add -U sqlite

# Clone repo
ADD . /opt/tracker/

WORKDIR /opt/tracker

RUN pip install -r requirements.txt

# Setup app
RUN ln -s /opt/tracker/setadmin.sh /usr/bin/setadmin

EXPOSE 8080
VOLUME "/srv/tracker"

ENTRYPOINT ["/opt/tracker/start.sh"]
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "3", "tracker:app"]
