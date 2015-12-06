#!/bin/bash

changed=0 && git pull | grep -q -v 'Already up-to-date.' && changed=1

if [ $changed = 1 ]; then

    pip install -r requirements.txt

    ENVIRONMENT=production
    LOCAL_USERNAME=`whoami`
    REVISION=`git log -n 1 --pretty=format:"%H"`

    ACCESS_TOKEN=719ef6f2566f46af9b849fdbc9d43680
    curl https://api.rollbar.com/api/1/deploy/ \
      -F access_token=$ACCESS_TOKEN \
      -F environment=$ENVIRONMENT \
      -F revision=$REVISION \
      -F local_username=$LOCAL_USERNAME \
      -k


    ACCESS_TOKEN=ccf521ba5e49428ebc79bd82b14587fa

    curl https://api.rollbar.com/api/1/deploy/ \
      -F access_token=$ACCESS_TOKEN \
      -F environment=$ENVIRONMENT \
      -F revision=$REVISION \
      -F local_username=$LOCAL_USERNAME \
      -k
fi
