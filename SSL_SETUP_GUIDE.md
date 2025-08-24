# SSL/HTTPS Setup Guide for mlcoe.live

## Overview
This guide will help you set up HTTPS with Let's Encrypt SSL certificates for your mlcoe.live website.

## Prerequisites
- Domain `mlcoe.live` must be pointing to your EC2 instance's public IP
- Ports 80 and 443 must be open in your EC2 security group
- Docker and docker-compose must be installed on your EC2 instance

## Method 1: Automated Setup (Recommended)

### Step 1: Upload files to EC2
Upload the following files to your EC2 instance:
- `setup_ssl.bat` (or `setup_ssl.sh` for Linux)
- Updated `nginx/conf.d/default.conf`
- Updated `docker-compose.yml`
- Updated `frontend/.env`

```bash
# Example scp commands (run from your local machine):
scp -i yoga.pem setup_ssl.sh ubuntu@mlcoe.live:/home/ubuntu/mlcoe/
scp -i yoga.pem nginx/conf.d/default.conf ubuntu@mlcoe.live:/home/ubuntu/mlcoe/nginx/conf.d/
scp -i yoga.pem docker-compose.yml ubuntu@mlcoe.live:/home/ubuntu/mlcoe/
scp -i yoga.pem frontend/.env ubuntu@mlcoe.live:/home/ubuntu/mlcoe/frontend/
```

### Step 2: Run the SSL setup script
SSH into your EC2 instance and run:

```bash
ssh -i yoga.pem ubuntu@mlcoe.live
cd mlcoe
chmod +x setup_ssl.sh

# IMPORTANT: Edit the script first to replace 'your-email@example.com' with your actual email
nano setup_ssl.sh
# Change: --email your-email@example.com
# To:     --email youremail@gmail.com

./setup_ssl.sh
```

## Method 2: Manual Setup

### Step 1: Create certificate directories
```bash
mkdir -p nginx/certbot/conf
mkdir -p nginx/certbot/www
```

### Step 2: Start with HTTP-only config
Create a temporary nginx config without SSL:

```bash
# Backup SSL config
cp nginx/conf.d/default.conf nginx/conf.d/default-ssl.conf

# Create temporary HTTP config
cat > nginx/conf.d/default.conf << 'EOF'
server {
    listen 80;
    server_name mlcoe.live;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://backend:5054;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
```

### Step 3: Start services
```bash
docker-compose up -d
```

### Step 4: Obtain SSL certificate
```bash
docker run --rm \
  -v $(pwd)/nginx/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/nginx/certbot/www:/var/www/certbot \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email youremail@gmail.com \
  --agree-tos \
  --no-eff-email \
  -d mlcoe.live
```

### Step 5: Restore SSL configuration
```bash
# Restore the SSL nginx config
cp nginx/conf.d/default-ssl.conf nginx/conf.d/default.conf

# Restart nginx
docker-compose restart nginx
```

## SSL Configuration Features

The new nginx configuration includes:

1. **HTTP to HTTPS redirect**: All HTTP traffic is automatically redirected to HTTPS
2. **Let's Encrypt integration**: Automatic certificate validation path
3. **Security headers**: HSTS, XSS protection, frame options, etc.
4. **Modern SSL settings**: TLS 1.2/1.3, secure ciphers, OCSP stapling
5. **Proxy headers**: Proper forwarding of client information to backend

## Certificate Renewal

SSL certificates from Let's Encrypt expire every 90 days. Use the renewal script:

```bash
# Manual renewal
./renew_ssl.sh

# Or add to crontab for automatic renewal (every day at noon)
crontab -e
# Add this line:
0 12 * * * /home/ubuntu/mlcoe/renew_ssl.sh
```

## Troubleshooting

### Common Issues:

1. **Certificate validation fails**:
   - Ensure domain points to your EC2 IP
   - Check security group allows ports 80/443
   - Verify nginx is running and accessible

2. **Mixed content warnings**:
   - Make sure all API calls use HTTPS
   - Update `REACT_APP_API_URL` to use https://

3. **Certificate not found**:
   - Check if certificate files exist in `nginx/certbot/conf/live/mlcoe.live/`
   - Verify the certificate generation process completed successfully

### Verification Commands:

```bash
# Check if certificates exist
ls -la nginx/certbot/conf/live/mlcoe.live/

# Check nginx configuration
docker-compose exec nginx nginx -t

# Check SSL certificate
openssl s_client -connect mlcoe.live:443 -servername mlcoe.live

# Check certificate expiry
echo | openssl s_client -connect mlcoe.live:443 -servername mlcoe.live 2>/dev/null | openssl x509 -noout -dates
```

## Final Steps

1. Update your frontend API URLs to use HTTPS
2. Test the website at https://mlcoe.live
3. Verify the SSL certificate is valid (green lock icon in browser)
4. Set up automatic certificate renewal

## Security Benefits

With HTTPS enabled, you get:
- ✅ Encrypted data transmission
- ✅ Authentication (visitors know they're on the real mlcoe.live)
- ✅ Data integrity (prevents tampering)
- ✅ SEO benefits (Google prefers HTTPS sites)
- ✅ Modern browser features (some APIs require HTTPS)
- ✅ User trust (green lock icon)
