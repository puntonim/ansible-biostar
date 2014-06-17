# Ansible deployment for Biostar-based projects

## 1. Overview
An Ansible playbook to automatize the deployment of a [Biostar-based](https://github.com/ialbert/biostar-central) project to an Amazon EC2 instance using Docker containers.

The tasks performed by the playbook are:

- create a new Amazon Security Group with open ports 22, 80, 443.
- create a new Amazon Key Pair with the public SSH key of the machine used to run Ansible.
- launch a new Amazon EC2 instance with the provided features.
- install Docker in the instance.
- Build and run a Docker container with PostgreSQL 9.3.
- Build and run a Docker container with [waitress](http://waitress.readthedocs.org/en/latest/) webserver running the provided codebase. 

## 2. Requirements
You need Ansible to be installed in the local machine.
The best way to install it is to start a Python 2.7 virtual environment and then:
```
pip install ansible
```

*Note*: during the deployment `boto` and `git` will be installed in the local machine (in the virtual environment in this case).

## 3. Usage
1. Clone this repo
2. Use your custom Django configuration:
  - copy the file [roles/docker_webapp/files/conf/production.env.template](https://github.com/nimiq/ansible-biostar/blob/master/roles/docker_webapp/files/conf/production.env.template) to `production.env` in the same folder and edit its `CUSTOM SECTION`.   
*Note*: `production.env` is ignored by git, so your passwords are safe!
  - edit the `CUSTOM SECTION` of [roles/docker_webapp/templates/biostar/settings/production.py.j2](https://github.com/nimiq/ansible-biostar/blob/master/roles/docker_webapp/templates/biostar/settings/production.py.j2)
3. Run the Ansible playbook, the basic usage is:
```
ansible-playbook site.yml --extra-vars "aws_access_key=YOUR_KEY aws_secret_key=YOUR_SECRET"
```


Ansible will output the IP address of the launched EC2 instance.
When the playbook is completed, you can then visit your new website at that address (on port 80).

On a t1.micro instance it takes about 12 mins.

*Note*: we are trying to move all the custom parts to `production.env` so that there is only one file to edit.

### 3.1. Playbook Advanced Arguments
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

Example:
```
ansible-playbook site.yml --extra-vars "aws_access_key=HKJHJK aws_secret_key=ghjGHJgjHGJ volume_size=8 postgresql_username=superman postgresql_password=fgHGFHGhgfh git_https_repo=https://github.com/my_user/biostar-central.git git_branch=new-deployment"
```

## 4. SSH Connections
You can SSH into the EC2 instance and into the 2 Docker containers.

### 4.1. SSH Into The EC2 Instance
```
ssh ubuntu@<INSTANCE_IP>
```
Ansible will output the instance IP.

### 4.2. SSH Into The Docker Containers
First SSH to the EC2 instance.  
Then you can either SSH into the webapp container:  
```
ssh root@127.0.0.1 -p 2222
```
Or SSH into the PostgreSQL container:  
```
ssh root@127.0.0.1 -p 2223
```

## 5. Container persistence
The PostgreSQL data directory and logs are stored in the EC2 instance at: `/home/ubuntu/workspace/docker-volumes/pgdata`.   
The codebase is at: `/home/ubuntu/workspace/biostar`.   
Logs of the web app are at: `/home/ubuntu/workspace/biostar/live/logs`.   
Django media files are at: `/home/ubuntu/workspace/biostar/live/export/media`.

## 6. Code Updates and Maintenance
### 6.1. Basic Code Updates
- SSH into the EC2 instance
- `cd /home/ubuntu/workspace/biostar`
- Do your code edits/updates, f.i.: `git pull`
- `docker webapp stop`
- `docker webapp start`

### 6.2. Proper Maintenance
- SSH into the webapp Docker container
- Stop the webapp Runit service, kill waitress-serve, source the env vars, do the mainainance, restart the webapp Runit service:
```
sv stop webapp
killall -9 waitress-serve

cd /root/biostar
source conf/docker.env
source /etc/container_environment.sh

# Do your maintenance, f.i.:
python manage.py my_maintenance

sv start webapp
```
*Note*: changes are saved into the container (by meaning if you create/edit a file, the new changes are saved in the container even after a `docker stop` - the new changes are lost only if you *remove* the container `docker rm webapp`)

## 7. Docker container start and stop
If you want to start/stop a webapp container first SSH to the EC2 instance.  
Then run:
```
docker stop webapp
docker start webapp
```

*Note*: stopping a container does NOT make you lose the data you edited in that container. Only removing a container wirh `docker rm webapp` makes you lose the data you edited in that container.

### 7.1. Restart webapp container
Restarting the webapp container causes `run_webapp.sh` to be run again.
This means that the following tasks will be executed:
- install requirements
- `source conf/production.env`
- create the database if it does not exist
- migrate the database
- if the database has just been created: load the fixture and rebuild the index
- collect static files
- run waitress-serve

Note that there is no `git pull`.
