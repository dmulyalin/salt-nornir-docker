# SaltStack Nornir Proxy Minion Docker

This repository contains files to start SaltStack Master and 
single instance of Nornir Proxy Minion using Docker containers.

**Why?** - To speed up the process of getting started with SaltStack Nornir Proxy Minion Network Automation

## Starting the environment

1. Install [Docker](https://docs.docker.com/engine/install/) and [Docker-Compose](https://docs.docker.com/compose/install/)
2. Install [GIT](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and clone this repository: `git clone https://github.com/dmulyalin/salt-nornir-docker.git` - or download manually from GitHub.
3. Modify Nornir Proxy Minion Pillar inventory to add network devices - see notes below
4. `cd` to folder with `docker-compose.yaml` file and start containers: `docker-compose up`, build takes 5-10 minutes
5. Drop into salt-master container shell and accept minion key: `docker exec -it salt-master bash`, `salt-key -a nrp1`

Start managing your devices

## Docker-Compose build and environment variables

Base image used to build containers is `centos:7`

Docker-compose makes use of these variables stored in `.env` file:

- `SALT_VERSION` - version of SaltStack to install, default is 3003, can be any of listed in [this repository](https://repo.saltproject.io/#rhel) for `REDHAT / CENTOS 7 PY3`
- `LOG_LEVEL` - logging level, default is 'debug' can be any of 'all', 'garbage', 'trace', 'debug', 'profile', 'info', 'warning', 'error', 'critical', 'quiet'
- `PROXY_ID` - Nornir Proxy Minion ID, default is 'nrp1'

Adjust above variables to meet your needs.

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
    ├── requirements.minion.txt
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
    
- `SALT/master` mounted under salt-master container `/etc/salt/` folder, contains master related configuration
- `SALT/proxy` mounted under salt-minion container `/etc/salt/` folder, contains proxy-minion related configuration
- `SALT/nornir_salt_data` mounted under salt-minion container `/var/salt-nornir/` folder for files produced by `tf` and `nr.learn` functions

## Python Packages Version

`requirements.minion.txt` indicates versions of Python packages that were tested and confirmed working together. 
This file used to install Python packages for minion container of all the modules that might be used by Salt 
Nornir Proxy Minion, edit requirements file to remove unnecessary packages or change versions.

For example, if no plans to use Netconf to manage devices can remove related packages from `requirements.minion.txt`
such as `ncclient` and `scrapli-netconf`.

Python version tested is 3.6

## Configuring Nornir Proxy Minion

Nornir Proxy Minion needs inventory data to manage devices - hostnames, IP addresses, credentials, device type etc. Because 
default proxy minion ID/Name is `nrp1`, need to populate inventory data in `SALT/master/pillar/nrp1.sls` pillar file. This file 
by default contains sample data to get your started:

```
proxy:
  proxytype: nornir

hosts:
  R1:
    hostname: 10.0.1.4
    platform: cisco_ios
    groups: [credentials]
          
groups: 
  credentials:
    username: nornir
    password: nornir
```

Modify it accordingly to list details for network devices you planning to manage.

Each time `SALT/master/pillar/nrp1.sls` pillar file modified, need to restart salt-minion container to pick up
updated inventory data - `docker restart salt-minion_nrp1`.

Platform attribute value is mandatory as it indicates what type of driver to use for device managing, here is a list where to find them:

- Netmiko `plaform` attribute [values](https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md#supported-ssh-device_type-values)
- NAPALM `plaform` attribute [values](https://napalm.readthedocs.io/en/latest/support/)
- Scrapli `plaform` attribute [values](https://scrapli.github.io/nornir_scrapli/user_guide/project_details/#supported-platforms)
- Scrapli-Netconf does not need `plaform` attribute but supports additional settings through `connection_options`
- Ncclient does not need `plaform` attribute but can support [device handlers](https://github.com/ncclient/ncclient#supported-device-handlers) through `connection_options`
- HTTP connection plugin does not need `plaform` attribute but supports additional settings through `connection_options`

<details><summary>Example: Cisco IOS Inventory Data for Netmiko and Napalm</summary>

```yaml
hosts:
  R1:
    hostname: 10.0.1.4
    platform: cisco_ios
    groups: [credentials]
          
groups: 
  credentials:
    username: nornir
    password: nornir
```
</details>

<details><summary>Example:Arista cEOS Inventory Data for Netmiko, Napalm, Scrapli, Scrapli-Netconf, Ncclient and HTTP connections</summary>

```yaml
hosts:
  ceos1:
    hostname: 10.0.1.4
    platform: arista_eos
    groups: [credentials, eos_params]
          
groups: 
  credentials:
    username: nornir
    password: nornir
    data:
      ntp_servers: ["3.3.3.3", "3.3.3.4"]
      syslog_servers: ["1.2.3.4", "4.3.2.1"] 
  eos_params:
    connection_options:
      scrapli:
        platform: arista_eos
        extras:
          auth_strict_key: False
          ssh_config_file: False
      scrapli_netconf:
        port: 830
        extras:
          ssh_config_file: True
          auth_strict_key: False
          transport: paramiko
          transport_options: 
            netconf_force_pty: False
      napalm:
        platform: eos
        optional_args:
          transport: http
          port: 80  
      ncclient:
        port: 830
        extras:
          allow_agent: False
          hostkey_verify: False
      http:
        port: 80
        transport: http
```
</details>

## Useful commands

Some useful commands.

| Command                                 | Description                                       |
|-----------------------------------------|---------------------------------------------------|
| docker exec -it salt-master bash        | Drop into salt-master container shell             |
| docker exec -it salt-minion bash        | Drop into salt-minion container shell             |
| docker restart salt-master              | Restart salt-master container                     |
| docker restart salt-minion_nrp1         | Restart salt-minion container                     |
| docker-compose stop                     | stop salt-minion and master containers altogether |
| docker-compose up                       | start salt-minion and master containers           |
| docker-compose build                    | rebuild containers                                |
| salt-key                                | manage proxy minions keys                         |
| salt nrp1 test.ping                     | verify that process is running                    |
| salt nrp1 nr.nornir stats               | check statistics for Nornir Proxy Minion          |
| salt nrp1 nr.nornir test                | test task to verify module operation              |
| salt nrp1 nr.nornir inventory           | to check Nornir inventory content                 |
| salt nrp1 nr.task nr_test               | test task to verify Nornir operation              |
| salt nrp1 nr.cli "show version"         | run show commands                                 |
| salt nrp1 nr.cfg "logging host 1.1.1.1" | edit configuration                                |

