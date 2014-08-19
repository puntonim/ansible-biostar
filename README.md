# Ansible deployment for Biostar-based projects

## 1. QuickStart

```
ansible-galaxy install nimiq.biostar
# Deploy to an Amazon EC2 instance:
ansible-playbook aws.yml --extra-vars 'aws_access_key=<YOUR_KEY> aws_secret_key=<YOUR_SECRET>'
# Or deploy to a Google Compute Engine instance (**TODO** not working yet):
ansible-playbook gce.yml --extra-vars 'gce_service_email=<SERVICE_ACCOUNT_EMAIL> gce_prj_name=<PRJ_NAME>'
```
**TODO**: fix, test and document GCE.

***
## Table of Contents

- [1. QuickStart](#1-quickstart)
- [2. Overview](#2-overview)
- [3. Requirements](#3-requirements)
- [4. Usage](#4-usage)
  - [4.1. Playbook Advanced Arguments](#41-playbook-advanced-arguments)
- [5. SSH Connections](#5-ssh-connections)
  - [5.1. SSH Into The EC2 Instance](#51-ssh-into-the-ec2-instance)
  - [5.2. SSH Into The Docker Containers](#52-ssh-into-the-docker-containers)
- [6. Containers Persistence and Logs](#6-container-persistence)
  - [6.1. `postgresql` container](#61-postgresql-container)
  - [6.2. `webapp` container](#62-webapp-container)
- [7. Code Updates and Maintenance](#7-code-updates-and-maintenance)
  - [7.1. Basic Code Updates](#71-basic-code-updates)
  - [7.2. Proper Maintenance](#72-proper-maintenance)
- [8. Docker container start and stop](#8-docker-container-start-and-stop)
  - [8.1. Restart webapp container](#81-restart-webapp-container)

***

## 2. Overview

An Ansible playbook to automate the deployment of a [Biostar-based](https://github.com/ialbert/biostar-central) project to an Amazon EC2 or GCE instances using Docker containers.

The tasks performed by the playbook are:

- Create security Group with open ports 22, 80, 443.
- Create an Amazon Key Pair with the public SSH key of the machine used to run Ansible.
- Launch an Amazon EC2 instance.
- Install Docker in the instance.
- Build and run a Docker container named `postgresql` with PostgreSQL 9.3.
- Build and run a Docker container named `webapp` with Nginx and [waitress](http://waitress.readthedocs.org/en/latest/) webserver running the provided codebase. 

## 3. Requirements

You need Ansible to be installed in the local machine.
The best way to install it is to start a Python 2.7 virtual environment and then:

```
pip install ansible
```

*Note*: during the deployment `boto` and `git` will be installed in the local machine (in the virtual environment in this case).

## 4. Usage

1. `git clone http://github.com/nimiq/ansible-biostar`
2. Use your custom Django configuration:
  - Copy the file [roles/docker_webapp/files/conf/production.env.template](https://github.com/nimiq/ansible-biostar/blob/master/roles/docker_webapp/files/conf/production.env.template) to `production.env` in the same folder and edit its `CUSTOM SECTION`.   
*Note*: `production.env` is ignored by git, so your passwords are safe!
  - Edit the `CUSTOM SECTION` of [roles/docker_webapp/templates/biostar/settings/production.py.j2](https://github.com/nimiq/ansible-biostar/blob/master/roles/docker_webapp/templates/biostar/settings/production.py.j2)
3. Run the Ansible playbook, the basic usage is:

```
ansible-playbook aws.yml --extra-vars 'aws_access_key=<YOUR_KEY> aws_secret_key=<YOUR_SECRET>'
```

Ansible will output the IP address of the launched EC2 instance.
When the playbook is completed, you can then visit your new website at that address (on port 80).

On a t1.micro instance it takes about 12 mins.

*Note*: we are trying to move all the custom parts to `production.env` so that there is only one file to edit.

### 4.1. Playbook Advanced Arguments

The are 2 groups of arguments for the playbook.

**Amazon AWS**: arguments to define the new EC2 instance that will be launched.

- `aws_access_key`: Amazon AWS access key. Mandatory.
- `aws_secret_key`: Amazon AWS secret key. Mandatory.
- `ssh_localhost_public_key_file_path`: A SSH public key to be added to the instance to accept SSH connections. Default: ~/.ssh/id_rsa.pub.
- `keypair`: Name to use when creating the new Amazon Key Pair. Default: biostar.
- `instance_type`: Type of the new instance. Default: t1.micro.
- `image`: Name of the AMI. Default: ami-896c96fe. 
- `group`: Name to use when creating the new Amazon Security Group. Default: biostar_SG_ireland. 
- `region`: A region name. Default: eu-west-1.
- `volume_size`: Size of the new volume in Gb. Default: 10.

**Biostar webapp**: arguments to setup the new Biostar webapp.

- `postgresql_username`: Username to use when creating the PostgreSQL database. Default: biostar.
- `postgresql_password`: Password to use when creating the PostgreSQL database. Default: biostar.
- `git_https_repo`: Codebase to use on GitHub. Default: https://github.com/ialbert/biostar-central.git.
- `git_branch`: Branch name. Default: master.
- `basic_auth_username`: Username to use for HTTP Basic authentication. If not provided, no HTTP Basic authentication is setup in Nginx.
- `basic_auth_password`: Password to use for HTTP Basic authentication in Nginx. If not provided, no HTTP Basic authentication is setup in Nginx.
- `load_sample_data`: Automatically loads sample data. Values: yes, no. Default: no.
- `nightly_reset_db`: Every night at 4am the db is flushed. If `load_sample_data` is active, the sample data are then imported. Values: yes, no. Default: no.

Example:

```
ansible-playbook aws.yml --extra-vars 'aws_access_key=ABCDE aws_secret_key=AbcDeFghiJ volume_size=8 postgresql_username=superman postgresql_password=kryptonite git_https_repo=https://github.com/my_user/biostar-central.git git_branch=new-deployment basic_auth_username=testuser basic_auth_password=mypassword'
```

## 5. SSH Connections

You can SSH into the EC2 instance and into the 2 Docker containers.

### 5.1. SSH Into The EC2 Instance

```
ssh ubuntu@<INSTANCE_IP>
```
Ansible will output the instance IP.

### 5.2. SSH Into The Docker Containers

First SSH to the EC2 instance.  
Then you can either SSH into the webapp container:  

```
ssh root@127.0.0.1 -p 2222
```

Or SSH into the PostgreSQL container:  

```
ssh root@127.0.0.1 -p 2223
```

## 6. Containers Persistence and Logs
### 6.1. `postgresql` container
The PostgreSQL data directory is in a shared volume stored in the EC2 host instance in: `/srv/docker-volumes/pgdata`.  
The log file is in: `/srv/docker-volumes/pgdata/logs`.

### 6.2. `webapp` container
The codebase is in a shared volume stored in the EC2 host instance in: `/srv/biostar-codebase`.   
In particular, Django media files are in: `/srv/biostar-codebase/live/export/media`.  
And Django static files are in: `/srv/biostar-codebase/live/export/static`.  
Log files are in: `/srv/biostar-codebase/live/logs/`.

## 7. Code Updates and Maintenance
### 7.1. Basic Code Updates

- SSH into the EC2 instance
- `cd /srv/biostar-codebase`
- Do your code edits/updates as user www-data, f.i.: `sudo -u www-data git pull`
- `docker stop webapp`
- `docker start webapp`

### 7.2. Proper Maintenance

- SSH into the webapp Docker container
- Stop the webapp Runit service, source the env vars, do the mainainance, restart the webapp Runit service:

```
sv stop webapp

cd /srv/biostar
source conf/production.env
source /etc/container_environment.sh

# Do your maintenance, f.i.:
python manage.py my_maintenance

sv start webapp
```

*Note*: changes are saved into the container (by meaning if you create/edit a file, the new changes are saved in the container even after a `docker stop` - the new changes are lost only if you *remove* the container `docker rm webapp`)

## 8. Docker container start and stop

If you want to start/stop a webapp container first SSH to the EC2 instance.  
Then run:

```
docker stop webapp
docker start webapp
```

*Note*: stopping a container does NOT make you lose the data you edited in that container. Only removing a container wirh `docker rm webapp` makes you lose the data you edited in that container.

### 8.1. Restart webapp container

Restarting the webapp container causes `run_webapp.sh` to be run again.
This means that the following tasks will be executed:

- Install requirements
- `source conf/production.env`
- Create the database if it does not exist
- Migrate the database
- If the database has just been created: load the fixture and rebuild the index
- Collect static files
- Run waitress-serve

Note that there is no `git pull`.
