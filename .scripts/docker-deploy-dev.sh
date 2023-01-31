#!/usr/bin

#/env bash

TARGET='dev'

cd ~/app || exit

ACTION='\033[1;90m'
NOCOLOR='\033[0m'

# Checking if we are on the dev branch

echo -e ${ACTION}Checking Git repo
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo target : ${TARGET}
echo branch : $BRANCH
if [ "$BRANCH" != ${TARGET} ]
then
  exit 0
fi

# Checking if the repository is up to date.

git fetch
HEADHASH=$(git rev-parse HEAD)
UPSTREAMHASH=$(git rev-parse ${TARGET}@{upstream})

#if [ "$HEADHASH" == "$UPSTREAMHASH" ]
#then
#  echo -e "${FINISHED}"Current branch is up to date with origin/${TARGET}."${NOCOLOR}"
#  exit 0
#fi

# If that's not the case, we pull the latest changes and we build a new image

git pull origin dev;

# Installing docker engine if not exists
if ! type docker > /dev/null
then
  echo "docker does not exist"
  echo "Start installing docker"
  sudo apt-get update
  sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
  sudo apt update
  apt-cache policy docker-ce
  sudo apt install -y docker-ce
fi

# Installing docker-compose if not exists
if ! type docker-compose > /dev/null
then
  echo "docker-compose does not exist"
  echo "Start installing docker-compose"
  sudo curl -L "https://github.com/docker/compose/releases/download/1.27.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
fi

docker-compose -f docker-compose.dev.yml up -d --build

exit 0;