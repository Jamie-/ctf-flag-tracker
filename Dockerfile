FROM debian:stretch
MAINTAINER Jamie Scott

# Update everything
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get dist-upgrade -y

# Install dependancies
RUN apt-get install -y python3 sqlite3 python3-pip make git
RUN pip3 install virtualenv

# Clone repo
RUN mkdir -p /opt/tracker
RUN git clone https://github.com/sotoncyber/ctf-flag-tracker.git /opt/tracker/

# Setup app
RUN cd /opt/tracker && make setup && make depends
RUN mkdir -p /srv/tracker

EXPOSE 5000
VOLUME "/srv/tracker"

CMD ["/bin/bash", "-c", "cd /opt/tracker && ./run.py"]
