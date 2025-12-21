# Deployment Documentation

## Project Information
- **Path**: `/home/evelynlu/EvelynApplications/PythonLearnHub`
- **Service Port**: 9090 (Nginx)
- **Deployment Info**: `/home/evelynlu/EvelynApplications/PythonLearnHub/deployment`

## Components
1. **Nginx**: Reverse proxy listening on port 9090.
   - Config: `/home/evelynlu/EvelynApplications/PythonLearnHub/deployment/nginx_app.conf`
   - Linked to: `/etc/nginx/sites-enabled/python-hub`

2. **Systemd Service**: Gunicorn managing the Flask app.
   - Service Name: `python-hub.service`
   - Config: `/home/evelynlu/EvelynApplications/PythonLearnHub/deployment/python-hub.service`
   - Socket: 127.0.0.1:8000

## Operations

### Restart Application
To apply code changes or restart the server, run the script:
```bash
/home/evelynlu/EvelynApplications/PythonLearnHub/deployment/restart_app.sh
```
Or manually:
```bash
sudo systemctl restart python-hub
```

### Logs
- **Application Logs**: `journalctl -u python-hub -f`
- **Nginx Error Logs**: `tail -f /var/log/nginx/error.log`
