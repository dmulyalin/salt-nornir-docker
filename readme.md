# SaltStack Nornir Proxy Minion Docker

This repository contains files to start SaltStack Master and 
single instance of Nornir Proxy Minion using Docker containers.

**Why?** - To speed up the process of getting started with SaltStack Nornir Proxy Minion 

## Starting the environment

1. Install [Docker](https://docs.docker.com/engine/install/), [Docker-Compose](https://docs.docker.com/compose/install/) and [GIT](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
2. Clone this repository: `git clone xxx`
3. Navigate to folder and build containers: `cd salt_nornir_docker`, `docker-compose build`
4. Modify Nornir Proxy Minion Pillar inventory to add network devices
5. Start containers: `docker-compose up`
6. Drop into salt-master shell, accept minion key and start managing your devices: `docker exec -it salt-master bash`, `salt-key -a nrp1`

