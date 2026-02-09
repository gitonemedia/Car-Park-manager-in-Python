# EC2 Setup Guide - Car Park Manager

## Prerequisites
- EC2 instance with Ubuntu 20.04 or later
- Security Group with ports 22 (SSH), 80 (HTTP), and 443 (HTTPS) open

## Step 1: Connect to EC2 and Update System
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip

sudo apt update
sudo apt upgrade -y
```

## Step 2: Install Dependencies
```bash
sudo apt install -y python3 python3-pip python3-venv nginx git
```

## Step 3: Clone Repository
```bash
cd /home/ubuntu
git clone https://github.com/one-media-asia/Car-Park-manager-in-Python.git
cd Car-Park-manager-in-Python
```

## Step 4: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-prod.txt
```

## Step 5: Configure Nginx
```bash
# Copy nginx configuration to sites-available
sudo cp nginx.conf /etc/nginx/sites-available/carpark

# Enable the site
sudo ln -s /etc/nginx/sites-available/carpark /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## Step 6: Create Systemd Service for Gunicorn
```bash
    
# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable carpark
sudo systemctl start carpark

# Check status
sudo systemctl status carpark
```

## Step 7: Verify Setup
```bash
# Check if Gunicorn is listening on port 5000
sudo netstat -tlpn | grep 5000

# Check if Nginx is listening on port 80
sudo netstat -tlpn | grep 80

# Test from EC2 instance
curl http://localhost
```

## Step 8: Access Your Application
Visit `http://your-ec2-public-ip` in your browser

## Logging and Troubleshooting

### View Gunicorn logs
```bash
sudo journalctl -u carpark -f
```

### View Nginx logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart services
```bash
sudo systemctl restart carpark
sudo systemctl restart nginx
```

## SSL/TLS for HTTPS (Optional)
If you need HTTPS, use AWS Certificate Manager or Let's Encrypt with Certbot:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Environment Variables
Set environment variables by editing the service file:
```bash
sudo nano /etc/systemd/system/carpark.service
# Add to [Service] section:
Environment="FLASK_SECRET_KEY=your-secret-key"
Environment="CARPARK_DB=/home/ubuntu/Car-Park-manager-in-Python/carpark.db"

sudo systemctl daemon-reload
sudo systemctl restart carpark
```
