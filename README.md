# CTF Flag Tracker #

## Installation ##

1. [Install docker](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-docker-ce).

2. Build container image from dockerfile:
```
docker build -t tracker https://raw.githubusercontent.com/Jamie-/ctf-flag-tracker/master/Dockerfile
```

3. Create data directory and add config file:
```
mkdir -p /srv/docker/tracker
wget https://raw.githubusercontent.com/Jamie-/ctf-flag-tracker/master/config.sample.json -O /srv/docker/tracker/config.json
```

4. Edit config file as required - `/srv/docker/tracker/config.json`.

5. Run docker container:
```
docker run --name=tracker --restart=always -p8080:8080 -v /srv/docker/tracker:/srv/tracker -d tracker
```

6. Create initial database:
```
docker exec -it tracker /bin/bash
# cd /opt/tracker
# make init-db
# exit
```
