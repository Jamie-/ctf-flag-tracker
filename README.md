# CTF Flag Tracker #

## Installation ##

[Install docker](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-docker-ce).

Build container image from dockerfile:
```
docker build -t tracker https://raw.githubusercontent.com/sotoncyber/ctf-flag-tracker/master/Dockerfile
```

Create data directory and add config file:
```
mkdir -p /srv/docker/tracker
wget https://raw.githubusercontent.com/sotoncyber/ctf-flag-tracker/master/config.sample.json -O /srv/docker/tracker/config.json
```

Run docker container:
```
docker run --name=tracker --restart=always -p5000:5000 -v /srv/docker/tracker:/srv/tracker -d tracker
```

Create initial database:
```
docker exec -it tracker /bin/bash
# cd /opt/tracker
# make init-db
# exit
```
