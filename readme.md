# SaltStack Nornir Proxy Minion Docker

This repository contains files to start SaltStack Master and a single instance of Nornir 
Proxy Minion using Docker containers.

**Why?** - To speed up the process of getting started with SaltStack Nornir Proxy Minion Network Automation.

## Starting the environment

Providing that you already installed [Docker](https://docs.docker.com/engine/install/), [Docker-Compose](https://docs.docker.com/compose/install/)
and [GIT](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git):
 
1. Clone this repository: `git clone https://github.com/dmulyalin/salt-nornir-docker.git`
2. `cd salt-nornir-docker` and start containers `docker-compose up`, build takes 5-10 minutes
3. Access salt-master shell `docker exec -it salt-master-3004 bash` and accept minion key `salt-key -a nrp1`

By default `nrp1` proxy pillar comes with configuration for always-on sandbox devices, as a result
can start experimenting with proxy-minion straight away.

Refer to wikipage for [examples](https://github.com/dmulyalin/salt-nornir-docker/wiki) on how to use 
Salt-Nornir proxy minion to manage network devices.

To start managing your devices add them to Nornir Proxy Minion Pillar inventory, see notes below, and
restart Proxy Minion container `docker restart salt-minion-3004-nrp1`

## Docker-Compose build and environment variables

Base image used to build containers is `centos:7`

Docker-compose makes use of these variables stored in `.env` file:

- `SALT_VERSION` - version of SaltStack to install, default is 3004 pulled from [REDHAT / CENTOS 7 PY3 repository](https://repo.saltproject.io/#rhel), other supported versions are - 3003 and 3002
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
    │   ├── templates
    │   └── rpc
    ├── salt_nornir_data
    └── proxy
        └── proxy
```        
    
Folders description:
    
- `SALT/master` mounted under salt-master container `/etc/salt/` folder, contains master related configuration
- `SALT/proxy` mounted under salt-minion container `/etc/salt/` folder, contains proxy-minion related configuration
- `SALT/salt_nornir_data` mounted under salt-minion container `/var/salt-nornir/` folder for files produced by `tf` and `nr.learn` functions

## Python Packages Version

Salt-Norir and Nornir-Salt installed using these extras:

- Salt-Master - `prodmin` i.e. `python3 -m pip install salt-nornir[prodmin]`
- Salt-Minion - `prodmax` i.e. `python3 -m pip install salt-nornir[prodmax]`

Python version used in container is 3.6.8

## Updating Docker Containers

It is recommended to re-build the container from scratch every time when
need to update them to different version of SaltStack or Salt-Nornir/Nornir-Salt.

SaltStack pillar and minion data saved on the volumes mounted from `SALT`
directory, no need to backup them unless planning to remove `SALT` directory.

Steps to update salt-nornir-docker containers are:

1. List containers to find out their names: `docker container ls`
2. Stop containers using names from `NAMES` column: `docker container stop salt-minion-3004-nrp1` and `docker container stop salt-master-3004`
3. Remove containers: `docker container rm salt-minion-3004-nrp1` and `docker container rm salt-master-3004`
4. Find `IMAGE ID` for `salt-nornir-docker` images: `docker image ls`
5. Remove images: `docker image rm -f 1c33fe852c44 6ebc37b30eef` - where `1c33fe852c44 6ebc37b30eef` are `IMAGE ID` from step 4
6. Adjust configuration - `.env` variables or `Docker` files - if required and re-build the containers: `docker-compose up`

## Configuring Nornir Proxy Minion

Nornir Proxy Minion needs inventory data to manage devices - hostnames, IP addresses, credentials, device type etc. Because 
default proxy minion ID/Name is `nrp1`, need to populate inventory data in `SALT/master/pillar/nrp1.sls` pillar file. 

Once ready, modify `nrp1.sls` pillar accordingly to list details for network devices you planning to manage.

Each time `SALT/master/pillar/nrp1.sls` pillar file modified, need to restart salt-minion container to pick up
updated inventory data - `docker restart salt-minion-3004-nrp1`.

Platform attribute value is mandatory as connections plugins need it to understand what type of driver to use for 
device managing, here is a list where to find `platform` attribute values:

- Netmiko `plaform` attribute [values](https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md#supported-ssh-device_type-values)
- NAPALM `plaform` attribute [values](https://napalm.readthedocs.io/en/latest/support/)
- Scrapli `plaform` attribute [values](https://scrapli.github.io/nornir_scrapli/user_guide/project_details/#supported-platforms)
- Scrapli-Netconf does not need `plaform` attribute but supports additional settings through `connection_options`
- Ncclient does not need `plaform` attribute but can support [device handlers](https://github.com/ncclient/ncclient#supported-device-handlers) through `connection_options`
- HTTP connection plugin does not need `plaform` attribute but supports additional settings through `connection_options`
- PyATS/Genie `os`/`platform` attribute values found in [Unicon docs](https://developer.cisco.com/docs/unicon/)

Inventory data for Nornir proxy Minion stored on Master machine in pillar files, below are examples of pillar files
to get started.

<details><summary>Example: Cisco IOS Inventory Data for Netmiko</summary>

```yaml
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
</details>

<details><summary>Example: Arista cEOS Inventory Data for Netmiko, Napalm, Scrapli, Scrapli-Netconf, Ncclient, PyGNMI, PyATS and HTTP RESTCONF connections</summary>

```yaml
proxy:
  proxytype: nornir
  
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
        port: 6020
        extras:
          transport: https
          verify: False
          base_url: "restconf/data"
          headers:
            Content-Type: "application/yang-data+json"
            Accept: "application/yang-data+json"
      pygnmi:
        port: 6030
        extras:
          insecure: True
      pyats:
        extras:
          devices:
            ceos1:
              os: eos
              credentials:
                default:
                  username: nornir
                  password: nornir
              connections:
                default:
                  protocol: ssh
                  ip: 10.0.1.4
                  port: 22
                vty_1:
                  protocol: ssh
                  ip: 10.0.1.4
                  pool: 3
```
</details>

<details><summary>Example: Cisco IOSXE/IOSXR/NXOS Inventory Data for Netmiko, Napalm, Scrapli, Scrapli-Netconf, Ncclient, PyATS and HTTP (IOSXE only) connections using always-on sandboxes</summary>

```yaml
proxy:
  proxytype: nornir
    
hosts:
  csr1000v-1:
    hostname: sandbox-iosxe-latest-1.cisco.com
    platform: cisco_ios
    username: developer
    password: C1sco12345
    port: 22
    connection_options:
      pyats:
        extras:
          devices:
            csr1000v-1:
              os: iosxe
              connections:
                default:
                  ip: 131.226.217.143
                  protocol: ssh
                  port: 22
      napalm:
        platform: ios
      scrapli:
        platform: cisco_iosxe
        extras:
          auth_strict_key: False
          ssh_config_file: False
      http:
        port: 443
        extras:
          transport: https
          verify: False
          base_url: "restconf/data"
          headers:
            Content-Type: "application/yang-data+json"
            Accept: "application/yang-data+json"
      ncclient:
        port: 830
        extras:
          allow_agent: False
          hostkey_verify: False
          device_params:
            name: iosxe
      scrapli_netconf:
        port: 830
        extras:
          transport: paramiko
          ssh_config_file: True
          auth_strict_key: False
          transport_options: 
            netconf_force_pty: False
  iosxr1:
    hostname: sandbox-iosxr-1.cisco.com
    platform: cisco_xr
    username: admin
    password: "C1sco12345"
    port: 22
    connection_options:
      pyats:
        extras:
          devices:
            iosxr1:
              os: iosxr
              connections:
                default:
                  ip: 131.226.217.150
                  protocol: ssh
                  port: 22
      napalm:
        platform: iosxr
      scrapli:
        platform: cisco_iosxr
        extras:
          auth_strict_key: False
          ssh_config_file: False
      ncclient:
        port: 830
        extras:
          allow_agent: False
          hostkey_verify: False
          device_params:
            name: iosxr
      scrapli_netconf:
        port: 830
        extras:
          ssh_config_file: True
          auth_strict_key: False
          transport_options: 
            netconf_force_pty: False
  sandbox-nxos-1.cisco:
    hostname: sandbox-nxos-1.cisco.com
    platform: nxos_ssh
    username: admin
    password: "Admin_1234!"
    port: 22
    connection_options:
      pyats:
        extras:
          devices:
            sandbox-nxos-1.cisco:
              os: nxos
              connections:
                default:
                  ip: 131.226.217.151
                  protocol: ssh
                  port: 22
      napalm:
        platform: nxos_ssh
      scrapli:
        platform: cisco_nxos
        extras:
          auth_strict_key: False
          ssh_config_file: False
      ncclient:
        port: 830
        extras:
          allow_agent: False
          hostkey_verify: False
          device_params:
            name: nexus
      scrapli_netconf:
        port: 830
        extras:
          ssh_config_file: True
          auth_strict_key: False
          transport_options: 
            netconf_force_pty: False   
```
</details>

## Useful commands

Some useful commands.

| Command                                 | Description                                       |
|-----------------------------------------|---------------------------------------------------|
| docker exec -it salt-master bash        | Drop into salt-master container shell             |
| docker exec -it salt-minion bash        | Drop into salt-minion container shell             |
| docker restart salt-master              | Restart salt-master container                     |
| docker restart salt-minion-3004-nrp1    | Restart salt-minion container                     |
| docker-compose stop                     | stop salt-minion and master containers altogether |
| docker-compose up                       | start salt-minion and master containers           |
| docker-compose build                    | rebuild containers                                |
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