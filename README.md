# Ansible deployment for Biostar-based projects

## Overview
An Ansible playbook to automatize the deployment of a [Biostar-based](https://github.com/ialbert/biostar-central) project to an Amazon EC2 instance.

The tasks performed by the playbook are:

- create a new Amazon Security Group with open ports 22, 80, 443.
- create a new Amazon Key Pair with the public SSH key of the machine used to run Ansible.
- launch a new Amazon EC2 instance with the provided features.
- install Docker in the instance.
- Build and run a Docker container with PostgreSQL 9.3.
- Build and run a Docker container with [waitress](http://waitress.readthedocs.org/en/latest/) webserver running the provided codebase. 

## Requirements
You need Ansible to be installed in the local machine.
The best way to install it is to start a Python 2.7 virtual environment and then:
```
pip install ansible
```

*Note*: during the deployment `boto` will be installed in the local machine (in the virtual environment in this case).

## Usage
The basic usage is:
```
ansible-playbook site.yml --extra-vars "aws_access_key=YOUR_KEY aws_secret_key=YOUR_SECRET"
```

Ansible will output the IP address of the launched EC2 instance.
When the playbook is completed, you can then visit your new website at that address (on port 80).

### Arguments
The are 2 groups of arguments.

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
- `git_https_repo`: Codebase to use on GitHub. Default: https://github.com/INCF/biostar-central.git.
- `git_branch`: Branch name. Default: master.

Example:
```
ansible-playbook site.yml --extra-vars "aws_access_key=HKJHJK aws_secret_key=ghjGHJgjHGJ volume_size=8 postgresql_username=superman postgresql_password=fgHGFHGhgfh git_https_repo=https://github.com/nimiq/biostar-central.git git_branch=new-deployment"
```

## SSH connections
You can SSH into the EC2 instance and into the 2 Docker containers.

### SSH into the EC2 instance
```
ssh ubuntu@<INSTANCE_IP>
```
Ansible will output the instance IP.

### SSH into the Docker containers
First SSH to the EC2 instance.  
Then you can either SSH into the webapp container:  
```
ssh root@127.0.0.1 -p 2222
```
Or SSH into the PostgreSQL container:  
```
ssh root@127.0.0.1 -p 2223
```
