#!/bin/bash

# Setup: Put the webhook in a text file.
#   touch webhook_url.txt; echo "XXXX" > webhook_url.txt  # replace secret

# Load webhook, get disk usage, build content, and post webhook.
export WEBHOOK_URL="`cat webhook_url.txt`"; echo $WEBHOOK_URL
export DU=`du -sh | cut -f 1`; echo $DU
export CONTENT='{"username": "climb_bot", "content": "Disk usage: '$DU'"}'; echo $CONTENT
curl -X POST -H "Content-Type: application/json" -d "$CONTENT" $WEBHOOK_URL
