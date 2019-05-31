# CTF Flag Tracker #

A CTF flag tracker for long-term tracking of multiple events or sessions for a group of people.
Designed and built for the [University of Southampton Cyber Security Society (SUCSS)](https://www.sucss.org/) to keep track of flags found by members during the academic year of events and sessions.

Has support for muliple events, teams per event and variable administration permissions so a user can be granted access to creating flags for their event.

Designed to run in Docker with Nginx up front.

No longer officially maintained but PRs and forks welcome!

## Installation ##

1. [Install docker](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-docker-ce)

2. Clone repository

```
$ git clone https://github.com/Jamie-/ctf-flag-tracker.git
```

3. Build container image from dockerfile:
```
$ cd ctf-flag-tracker
$ docker build -t tracker .
```

4. Create data directory and add config file:
```
$ mkdir -p /srv/docker/tracker
$ cp config.sample.json /srv/docker/tracker/config.json
```

5. Edit config file as required - `/srv/docker/tracker/config.json`. All strings available under `VIEW_CONFIG` are shown but none are required. If you want a string to be default or hidden, omit it's entry.

6. Run docker container:
```
$ docker run --name=tracker --restart=always -p8080:8080 -v /srv/docker/tracker:/srv/tracker -d tracker
```

7. Create initial admin user:
Visit the app in your browser and create an account `http://<ip_address>:8080/register`
After creating an account, grant it admin priviledges as below:
```
$ docker exec -it tracker sh
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
