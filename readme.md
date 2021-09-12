# SaltStack Nornir Proxy Minion Docker

This repository contains files to start SaltStack Master and 
single instance of Nornir Proxy Minion using Docker containers.

**Why?** - To speed up the process of getting started with SaltStack Nornir Proxy Minion 

## Starting the environment

1. Install [Docker](https://docs.docker.com/engine/install/), [Docker-Compose](https://docs.docker.com/compose/install/) and [GIT](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
2. Clone this repository: `git clone https://github.com/dmulyalin/salt-nornir-docker.git`
3. Modify Nornir Proxy Minion Pillar inventory to add network devices - see notes below
4. Move to folder with `docker-compose.yaml` file and start containers: `docker-compose up`
6. Drop into salt-master shell and accept Nornir Proxy Minion key: `docker exec -it salt-master bash`, `salt-key -a nrp1`
7. Start managing your devices

## Docker-Compose build and environment variables

Base image used to build containers is `centos:7`

Docker-compose makes use of these variables stored in `.env` file:

- `SALT_VERSION` - version of SaltStack to install, default is 3003, can be any of listed in [this repository](https://repo.saltproject.io/#rhel) for `REDHAT / CENTOS 7 PY3`
- `LOG_LEVEL` - loggin level, default is 'debug' can be any of 'all', 'garbage', 'trace', 'debug', 'profile', 'info', 'warning', 'error', 'critical', 'quiet'
- `PROXY_ID` - Nornir Proxy Minion ID, default is 'nrp1'

Feel free to adjust them as per your needs.

## Folders structure

Folders structure:

```
salt_nornir_docker/
├── docker-compose.yaml
├── readme.md
├── .env
└── SALT
    ├── Dockerfile.master
    ├── Dockerfile.minion
    ├── master
    │   ├── master
    │   ├── pillar
    │   │   ├── nrp1.sls
    │   │   └── top.sls
    │   ├── states
    │   └── templates
    ├── nornir_salt_data
    └── proxy
        └── proxy
```		
	
Folders description:
	
- `SALT/master` mounted under salt-master container `/etc/salt/` folder and contains all master related configuration
- `SALT/proxy` mounted under salt-minion container `/etc/salt/` folder and contains all proxy-minion related configuration
- `SALT/nornir_salt_data` mounted under salt-minion container `/var/salt-nornir/` folder and contains files produced by `tf` and `nr.learn` functions

## Configuring Nornir Proxy Minion

Nornir Proxy Minion needs inventory data to manage devices - hostnames, IP addresses, credentials, device type etc. Because 
default proxy minion ID/Name is `nrp1`, need to populate inventory data in `SALT/master/pillar/nrp1.sls` pillar file. This file 
by default contains sample data to get your started:

```
proxy:
  proxytype: nornir

hosts:
  ceos1:
    hostname: 10.0.1.4
    platform: cisco_ios
    groups: [credentials]
          
groups: 
  credentials:
    username: nornir
    password: nornir
```

Modify it accordingly to list details for network devices to manage them.

Each time `SALT/master/pillar/nrp1.sls` pillar file modified, need to restart salt-minion container to pick up
updated inventory data - `docker restart salt-minion_nrp1`. Alternatively, can run `nr_refresh` task - `salt nrp1 nr.task nr_refresh`
from master.

## Useful commands

Some useful commands.

| Command                           | Description                                       |
|-----------------------------------|---------------------------------------------------|
| docker exec -it salt-master bash  | Drop into salt-master container shell             |
| docker exec -it salt-minion bash  | Drop into salt-minion container shell             |
| docker restart salt-master        | Restart salt-master container                     |
| docker restart salt-minion_nrp1   | Restart salt-minion container                     |
| docker-compose stop               | stop salt-minion and master containers altogether |
| docker-compose up                 | start salt-minion and master containers           |
| docker-compose build              | rebuild containers                                |

