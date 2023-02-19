#!/usr/bin/env bash

set -eo pipefail

# system libraries
sudo yum -y update
sudo yum -y install python3 python3-pip python3-devel wget nginx
sudo amazon-linux-extras install epel -y
sudo yum -y install gcc openssl-devel bzip2-devel libffi-devel zlib-devel
sudo tee /etc/yum.repos.d/pgdg.repo<<EOF
[pgdg14]
name=PostgreSQL 14 for RHEL/CentOS 7 - x86_64
baseurl=http://download.postgresql.org/pub/repos/yum/14/redhat/rhel-7-x86_64
enabled=1
gpgcheck=0
EOF
sudo yum makecache
sudo yum install postgresql14 postgresql14-server -y

# export variables
export POSTGRES_USER=${POSTGRES_USER}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
export POSTGRES_DB=${POSTGRES_DB}
export POSTGRES_PORT=${POSTGRES_PORT}
export POSTGRES_HOST=${POSTGRES_HOST}

# Create postgres user
sudo postgresql-14-setup initdb
sudo systemctl enable --now postgresql-14
sudo su - postgres <<EOF
psql -c "CREATE database ${POSTGRES_DB}"
psql -c "CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};"
psql -c "\du"
EOF
sudo sed -i 's/\(scram-sha-256\|ident\|peer\)/md5/g' /var/lib/pgsql/14/data/pg_hba.conf
sudo systemctl restart postgresql-14


# Install Python 3.9
wget https://www.python.org/ftp/python/3.9.6/Python-3.9.6.tgz
tar -xzf Python-3.9.6.tgz
cd Python-3.9.6
./configure --enable-optimizations
sudo make
sudo make install


# Install requirements
cd /home/ec2-user/webapp
pip3 install --upgrade pip
pip3 install -r requirements/local.txt

# webapp system service
sudo cp packer/webapp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable webapp.service
sudo systemctl start webapp.service

# Install nginx
sudo amazon-linux-extras list | grep nginx
sudo amazon-linux-extras enable nginx1
sudo yum clean metadata
sudo yum -y install nginx
sudo systemctl enable nginx
sudo cp packer/nginx.conf /etc/nginx/
sudo systemctl restart nginx
sudo systemctl reload nginx

