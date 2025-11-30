#!/bin/sh
set -e

sudo apt-get update -y
sudo apt-get upgrade -y -o Dpkg::Options::="--force-confnew"

sudo apt update -y
sudo apt upgrade -y -o Dpkg::Options::="--force-confnew"

sudo apt install -y -o Dpkg::Options::="--force-confnew" git

# De https://docs.docker.com/engine/install/debian/#install-using-the-repository
sudo apt update -y
sudo apt install -y -o Dpkg::Options::="--force-confnew" ca-certificates curl
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

sudo apt update -y
sudo apt install -y -o Dpkg::Options::="--force-confnew" docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Docker se inicia automaticamente tras la isntalación pero en algunos sitemas no es así
sudo systemctl start docker
sudo systemctl enable docker

# Clonamos el repo dle proyecto
git clone https://github.com/mateonation/pipeline-mongodb-docker.git

sudo apt install -y -o Dpkg::Options::="--force-confnew" python3 python3-venv python3-pip
cd ./pipeline-mongodb-docker
python3 -m venv venv
. venv/bin/activate
pip install --no-input pandas cassandra-driver pymongo mysql-connector-python matplotlib redis

# Arrancamos el docker de producción
sudo docker compose -f docker-compose.yaml -f docker-compose.production.yaml up -d
