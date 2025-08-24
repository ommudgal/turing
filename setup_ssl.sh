#!/bin/bash

# SSL Setup Script for mlcoe.live
echo "Setting up SSL certificates for mlcoe.live..."

# Create necessary directories
mkdir -p nginx/certbot/conf
mkdir -p nginx/certbot/www

# Start nginx without SSL first (for initial certificate generation)
echo "Starting nginx in HTTP mode for certificate generation..."

# Create temporary HTTP-only nginx config
cat > nginx/conf.d/temp.conf << 'EOF'
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

# Backup the SSL config
mv nginx/conf.d/default.conf nginx/conf.d/default-ssl.conf

# Use temp config
mv nginx/conf.d/temp.conf nginx/conf.d/default.conf

# Start the services
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Obtain SSL certificate
echo "Obtaining SSL certificate..."
docker run --rm \
  -v $(pwd)/nginx/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/nginx/certbot/www:/var/www/certbot \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d mlcoe.live

# Check if certificate was obtained successfully
if [ -f "nginx/certbot/conf/live/mlcoe.live/fullchain.pem" ]; then
    echo "Certificate obtained successfully!"
    
    # Restore SSL configuration
    mv nginx/conf.d/default.conf nginx/conf.d/temp.conf
    mv nginx/conf.d/default-ssl.conf nginx/conf.d/default.conf
    
    # Restart nginx with SSL configuration
    docker-compose restart nginx
    
    echo "SSL setup complete! Your site should now be accessible at https://mlcoe.live"
else
    echo "Failed to obtain certificate. Please check the logs and try again."
    exit 1
fi

# Setup auto-renewal
echo "Setting up auto-renewal..."
cat > renew_ssl.sh << 'EOF'
#!/bin/bash
docker run --rm \
  -v $(pwd)/nginx/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/nginx/certbot/www:/var/www/certbot \
  certbot/certbot renew --quiet

docker-compose restart nginx
EOF

chmod +x renew_ssl.sh

echo "SSL setup complete!"
echo "- Your site is now available at https://mlcoe.live"
echo "- Automatic HTTP to HTTPS redirect is enabled"
echo "- Certificate auto-renewal script created: renew_ssl.sh"
echo "- Add the following to your crontab for automatic renewal:"
echo "  0 12 * * * /path/to/your/project/renew_ssl.sh"
