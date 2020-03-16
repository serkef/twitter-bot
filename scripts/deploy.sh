#!/bin/bash

git pull
BUILD_TAG=$(git rev-parse HEAD)
docker build -t twitter-bot:${BUILD_TAG} .
docker stop breaking-bot
docker rm breaking-bot
docker run --rm --env-file=.env --name breaking-bot twitter-bot:${BUILD_TAG}
