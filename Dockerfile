FROM debian:stretch
MAINTAINER Jamie Scott

# Update everything
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get dist-upgrade -y

# Install dependancies
RUN apt-get install -y python3 sqlite3 python3-pip python3-venv make git

# Clone repo
RUN mkdir -p /opt/tracker
RUN git clone https://github.com/Jamie-/ctf-flag-tracker.git /opt/tracker/

# Setup app
RUN cd /opt/tracker && make setup && make depends
RUN mkdir -p /srv/tracker
RUN ln -s /opt/tracker/setadmin.sh /usr/bin/setadmin

EXPOSE 8080
VOLUME "/srv/tracker"

CMD ["/opt/tracker/start.sh"]
