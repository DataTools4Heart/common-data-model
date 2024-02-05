#!/bin/bash

docker compose -f common-data-model/docker/docker-compose-onfhir.yml --project-directory ./ -p dt4h-onfhir up -d
