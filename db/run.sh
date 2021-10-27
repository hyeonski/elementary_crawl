#!/bin/bash

docker-compose up --build -d
sleep 15
mysql --host 127.0.0.1 -u root -p1234 < ./insert_data.sql