# deployment

Deployment utils

## I. Usage

### 1. Install 'deploy utils'
```bash
if ! type -p /usr/bin/git > /dev/null; then sudo apt -y update; sudo apt -y install git; fi
if [[ ! -d /data/deployment ]]; then sudo mkdir -p /data; sudo chown $(whoami) /data; git clone git@github.com:ci-and-cd/deployment.git /data/deployment; fi
(cd /data/deployment; git checkout master; git pull)
#export APT_REPOSITORY_DOCKER="https://download.docker.com/linux/ubuntu"
#export APT_REPOSITORY_DOCKER="https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/ubuntu"
/data/deployment/bin/deploy install -v
exit;
```

### 2. Set up environment (instance configs)
```bash
deploy environment topinfra-nz-dev
# e.g. 
#or
#deploy environment git@github.com:ci-and-cd/topinfra-nz-dev.git
deploy environments
```

### 3. Make sure that you can access git repositories (for downloading docker-compose_service.yml) and docker registry.

```bash
# find your token at Github (https://github.com/settings/tokens) or Gitlab (https://gitlab.com/profile/account)
export CI_OPT_GIT_AUTH_TOKEN={your_gitlab_private_token}

# need username and password
docker login https://docker.io/v2/
# or private registry e.g.
docker login docker-registry.infra.top
```

### 4. Deploy service instances
```bash
#deploy docker-compose {instance} up/down {options}
# e.g.
deploy docker-compose standalone.eureka up -d -v
```

## II. Commands and options


### 1. Commands always available

commands
> list all commands.

environment
> get current environment.

environment {environment}
environment {environment_git_url}
> set environment (clone environment repository to local).

environment -c latest
> update local environment repository to latest commit.

environment -c {commit_id}
> checkout local environment repository to given {commit_id}.

environments
> list all environments (local repositories) in .config/environments.


### 2. Commands only available after environment is setup

clean
> remove all environment repositories in .config/environments.

clean {environment} 
> remove specific environment repository. double tab to auto complete {environment}.

current-host
> get current host ip address.

docker-compose {instance}
> run docker-compose commands on given instance. double tab to auto complete {instance}.
double tab to auto complete {instance}.

doctor
> check configs in environment repository.

fix-permissions
> fix ownership/permission for all files/directories in environment repositories (in .config/environments) and instances directories (in instances). 

fix-permissions {directory}
> fix ownership/permission for all files/directories in given {directory}.

fix-permissions {instance}
> fix ownership/permission for all files/directories in instances/{environment}/{instance}.
double tab to auto complete {instance}.

install
> install deployment utils on current host.

instance-deploy-config {instance}
> prepare deploy config for given {instance}.
double tab to auto complete {instance}.

instance-dir {instance}
> get directory of given {instance} (instances/{environment}/{instance}).
double tab to auto complete {instance}.

instance-properties {instance}
> get instance.properties path of given {instance} (.config/environments/{environment}/{host}/{service_name}/{instance}/instance.properties).
double tab to auto complete {instance}.

instance-properties-dir {instance}
> get instance.properties's parent directory path of given {instance} (.config/environments/{environment}/{host}/{service_name}/{instance}).
double tab to auto complete {instance}.

instance-service {instance}
> get service name of given {instance}.
double tab to auto complete {instance}.

instance-variables {instance}
> get instance.env file path (.config/environments/{environment}/{host}/{service_name}/{instance}/instance.env).
instance.env is combination of environment.properties, host.properties, {service_name}.properties and instance.properties.
double tab to auto complete {instance}.

list
> list all instance directories in instances/{environment}.

normalize-instance {instance}
> normalize short instance coordinate to normal (long) instance coordinate.
e.g. standalone.config-server to 192.168.1.1/config-server/standalone.
double tab to auto complete {instance}.

search
> find instances that run on current host.

search -a
> find all instances that run on all hosts.

search-named-instances
> find named instances that run on current host.

search-named-instances -a
> find all named instances that run on all hosts.

search-standalone-instances
> find standalone instances that run on current host.

search-standalone-instances -a
> find all standalone instances that run on all hosts.

update or update -c latest
> update deployment utils to latest commit.

update -c {commit_id}
> checkout deployment utils repository to given {commit_id}.


### 3. Options

-a --all
> list all for search or list commands

-c --commit
> latest or commit-id for environment command

-s --short
> use short instance coordinate for search or list commands

-v --verbose
> verbose outputs to stderr for all commands


## Move Docker data directory

```bash
sudo service docker stop
sudo tar -zcC /var/lib docker > /data/var_lib_docker-backup-$(date +%s).tar.gz
sudo mv /var/lib/docker /data/docker
```

see: https://stackoverflow.com/questions/24309526/how-to-change-the-docker-image-installation-directory/34731550#34731550

```bash
sudo ln -s /data/docker /var/lib/docker
```

or

```bash
sudo vi /etc/docker/daemon.json
```
```json
{
  "graph": "/data/docker",
  "storage-driver": "overlay"
}
```
```bash
sudo service docker start
```

## Build virtualenv

```bash
virtualenv -p /usr/bin/python2.7 venv_$(uname -s)
source venv_$(uname -s)/bin/activate

pip install networkx
#pip install matplotlib=2.2.3
# On OSX
# mkdir -p ~/.matplotlib
# echo 'backend: TkAgg' | tee ~/.matplotlib/matplotlibrc
#pip install pygraphviz
#pip install pydot

pip freeze > requirements.txt
pip install -r requirements.txt

deactivate
```
