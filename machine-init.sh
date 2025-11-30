#!/bin/sh

sudo apt-get update
sudo apt-get upgrade

sudo apt update
sudo apt upgrade

sudo apt install git

# De https://docs.docker.com/engine/install/debian/#install-using-the-repository
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Docker se inicia automaticamente tras la isntalación pero en algunos sitemas no es así
sudo systemctl start docker
sudo systemctl enable docker

# Clonamos el repo dle proyecto
git clone https://github.com/mateonation/pipeline-mongodb-docker.git

# Arrancamos el docker de producción
sudo docker compose -f ./pipeline-mongodb-docker/docker-compose.yaml -f ./pipeline-mongodb-docker/docker-compose.production.yaml up -d
