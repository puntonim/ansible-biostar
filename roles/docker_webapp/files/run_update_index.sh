#!/bin/bash

cd /root/biostar
source conf/production.env
source /etc/container_environment.sh
RES=`python manage.py update_index`
echo `date` - $RES >> /root/biostar/live/logs/rebuild_index.log