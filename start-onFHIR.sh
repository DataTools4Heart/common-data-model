#!/usr/bin/env bash

java -jar -Dmongodb.embedded=true -Dconfig.file=onfhir.conf onfhir-server-standalone.jar

