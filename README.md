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

4. Edit config file as required - `/srv/docker/tracker/config.json`. All strings available under `VIEW_CONFIG` are shown but none are required. If you want a string to be default or hidden, omit it's entry.

5. Run docker container:
```
docker run --name=tracker --restart=always -p8080:8080 -v /srv/docker/tracker:/srv/tracker -d tracker
```

6. Create initial admin user:
Visit the app in your browser and create an account `http://<ip_address>:8080/register`
After creating an account, grant it admin priviledges as below
```
$ docker exec -it tracker /bin/bash
# setadmin <username>
# exit
```

### Running Behind Nginx Proxy ###
Use this snippet inside your `server {...}` block. The most important part is `proxy_redirect` when using SSL as without this, redirects are broken!
```
location / {
    proxy_pass http://localhost:8080;
    proxy_redirect http:// $scheme://;
    proxy_set_header HOST $http_host;
}
```
