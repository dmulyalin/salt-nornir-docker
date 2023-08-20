# SaltStack Nornir Proxy Minion Docker

This repository contains files to build and start a Docker container running 
SaltStack Master, Salt-API and Salt Proxy Minion.

**Why?** - To speed up the process of getting started with SaltStack Nornir Proxy Minion Network Automation.

## Starting the environment

Providing that you already installed [Docker](https://docs.docker.com/engine/install/), [Docker Compose](https://docs.docker.com/compose/install/)
and [GIT](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git):
 
1. Clone this repository: `git clone https://github.com/dmulyalin/salt-nornir-docker.git`
2. `cd salt-nornir-docker` and start container `docker compose up`, build takes 5-10 minutes
3. Access container shell `docker exec -it saltstack bash` and accept minion key `salt-key -a nrp1`

By default `nrp1` proxy pillar comes with configuration for always-on sandbox devices, as a result
can start experimenting with proxy-minion straight away.

Refer to wiki page for [examples](https://github.com/dmulyalin/salt-nornir-docker/wiki) on how to use 
Salt-Nornir proxy minion to manage network devices.

To start managing your devices add them to Nornir Proxy Minion Pillar inventory, see notes below, and
restart Proxy Minion container `docker restart saltstack`

## Docker Compose build and environment variables

Base image used to build container is `python:3.9.7-slim-bullseye`

Docker compose makes use of these variables stored in `.env` file:

- `SALT_VERSION` - version of SaltStack to install, default is 3006, other tested versions are - 3005, 3004, 3003 and 3002
- `LOG_LEVEL` - logging level, default is 'debug' can be any of 'all', 'garbage', 'trace', 'debug', 'profile', 'info', 'warning', 'error', 'critical', 'quiet'
- `PROXY_ID` - Nornir Proxy Minion ID, default is 'nrp1'
- `SALT_MASTER` - True or False, if True will start salt-master process inside the container
- `SALT_API` - True or False, if True will start salt-api process inside the container if `SALT_MASTER` set to True
- `SALT_PROXY` - True or False, if True will start salt-proxy minion process inside the container

Adjust above variables to meet your needs.

## Folders structure

Folders structure:

```
salt_nornir_docker/
├── docker-compose.yaml
├── readme.md
└── SALT
    ├── Dockerfile.saltstack
    ├── saltinit.py
    ├── salt_nornir_data
    │   └── placeholder
    └── saltstack
        ├── master
        ├── pillar
        │   ├── nrp1.sls
        │   └── top.sls
        ├── pki
        ├── proxy
        ├── rpc
        │   └── oc_interface.xml
        ├── states
        └── templates
```        
    
Folders description:
    
- `SALT/saltstack` mounted under container `/etc/salt/` folder, contains master and proxy related configuration
- `SALT/salt_nornir_data` mounted under container `/var/salt-nornir/` folder for files produced by `tf` and `nr.learn` functions
- `SALT/saltstack/master` - salt-master configuration file
- `SALT/saltstack/proxy` - salt-proxy configuration file

## Python Packages Version

Salt-Norir and Nornir-Salt installed using these extras:

- `prodmaxmaster` i.e. `python3 -m pip install salt-nornir[prodmaxmaster]`
- `prodmaxminion` i.e. `python3 -m pip install salt-nornir[prodmaxminion]`

Python version used in a container is 3.9.7

## Updating Docker Container

It is recommended to re-build the container from scratch every time when
need to update them to different version of SaltStack or Salt-Nornir/Nornir-Salt.

SaltStack pillar and minion data saved on the volumes mounted from `SALT`
directory, it is recommended to back up `SALT` directory before proceeding.

Steps to update salt-nornir-docker container are:

1. Stop and remove saltstack container: `docker compose down`
2. Rebuild image: `docker compose build --no-cache`
3. Start container: `docker compose up`

## Configuring Nornir Proxy Minion

Nornir Proxy Minion needs inventory data to manage devices - hostnames, IP addresses, credentials, device type etc. Because 
default proxy minion ID/Name is `nrp1`, need to populate inventory data in `SALT/saltstack/pillar/nrp1.sls` pillar file. 

Once ready, modify `nrp1.sls` pillar accordingly to list details for network devices you planning to manage.

Each time `SALT/saltstack/pillar/nrp1.sls` pillar file modified, need to restart saltstack to pick up
updated inventory data - `docker restart saltstack`.

Platform attribute value is mandatory as connections plugins need it to understand what type of driver to use for 
device managing, here is a list where to find `platform` attribute values:

- Netmiko `platform` attribute [values](https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md#supported-ssh-device_type-values)
- NAPALM `platform` attribute [values](https://napalm.readthedocs.io/en/latest/support/)
- Scrapli `platform` attribute [values](https://scrapli.github.io/nornir_scrapli/user_guide/project_details/#supported-platforms)
- Scrapli-Netconf does not need `platform` attribute but supports additional settings through `connection_options`
- Ncclient does not need `platform` attribute but can support [device handlers](https://github.com/ncclient/ncclient#supported-device-handlers) through `connection_options`
- HTTP connection plugin does not need `platform` attribute but supports additional settings through `connection_options`
- PyATS/Genie `os`/`platform` attribute values found in [Unicon docs](https://developer.cisco.com/docs/unicon/)

Inventory data for Nornir proxy Minion stored on Master machine in pillar files, refer documentation for
examples - [Pillar and Inventory Examples](https://salt-nornir.readthedocs.io/en/latest/Pillar%20and%20Inventory%20Examples.html)

# Enabling and working with REST API

If enabled with `SALT_API` environment variable, Salt-API configured to 
listen for HTTP requests on all host's interfaces on TCP port 8001.

Example how to use CURL to run `salt nrp1 nr.nornir version` command over REST 
API from the host:

```
curl http://127.0.0.1:8001/run \
    -H 'Accept: application/x-yaml' \
    -d client='local' \
    -d tgt='nrp1' \
    -d fun='nr.nornir' \
    -d arg='version' \
    -d username='saltuser' \
    -d password='saltpass' \
    -d eauth='sharedsecret'
```

Refer to SaltStack 
[REST CHERRYPY documentation](https://docs.saltproject.io/en/latest/ref/netapi/all/salt.netapi.rest_cherrypy.html) 
on how to enable HTTPS and harden API setup.

## Useful commands

Some useful commands.

| Command                                 | Description                                       |
|-----------------------------------------|---------------------------------------------------|
| docker exec -it saltstack bash          | Drop into container bash shell                    |
| docker restart saltstack                | Restart saltstack container                       |
| docker compose stop                     | stop saltstack container altogether               |
| docker compose up                       | start saltstack container                         |
| docker compose build                    | rebuild container                                 |
| salt-key                                | manage proxy minions keys                         |
| salt nrp1 test.ping                     | verify that process is running                    |
| salt nrp1 nr.nornir stats               | check statistics for Nornir Proxy Minion          |
| salt nrp1 nr.nornir test                | test task to verify module operation              |
| salt nrp1 nr.nornir inventory           | to check Nornir inventory content                 |
| salt nrp1 nr.nornir hosts               | to list managed hosts names                       |
| salt nrp1 nr.task nr_test               | test task to verify Nornir operation              |
| salt nrp1 nr.cli "show version"         | run show commands                                 |
| salt nrp1 nr.cfg "logging host 1.1.1.1" | edit configuration                                |

## Additional resources

Documentation is a good place to continue:

- [Salt-Nornir documentation](https://salt-nornir.readthedocs.io/)
- [Nornir-Salt documentation](https://nornir-salt.readthedocs.io/)
- [Nornir documentation](https://nornir.readthedocs.io/)
- [SaltStack documentation](https://docs.saltproject.io/en/getstarted/)

Salt-Nornir Proxy Minion [usage examples](https://github.com/dmulyalin/salt-nornir-docker/wiki)