#!/bin/bash
set -e
echo "Restarting Gunicorn Service..."
sudo systemctl restart python-hub
echo "Reloading Nginx..."
sudo systemctl reload nginx
echo "Done! App should be live on port 9090."
