@echo off
echo Setting up SSL certificates for mlcoe.live...

REM Create necessary directories
if not exist "nginx\certbot\conf" mkdir nginx\certbot\conf
if not exist "nginx\certbot\www" mkdir nginx\certbot\www

echo Creating temporary HTTP-only nginx config...

REM Create temporary HTTP-only nginx config
(
echo server {
echo     listen 80;
echo     server_name mlcoe.live;
echo.
echo     location /.well-known/acme-challenge/ {
echo         root /var/www/certbot;
echo     }
echo.
echo     location / {
echo         proxy_pass http://frontend:80;
echo         proxy_set_header Host $host;
echo         proxy_set_header X-Real-IP $remote_addr;
echo         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
echo         proxy_set_header X-Forwarded-Proto $scheme;
echo     }
echo.
echo     location /api/ {
echo         proxy_pass http://backend:5054;
echo         proxy_set_header Host $host;
echo         proxy_set_header X-Real-IP $remote_addr;
echo         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
echo         proxy_set_header X-Forwarded-Proto $scheme;
echo     }
echo }
) > nginx\conf.d\temp.conf

REM Backup the SSL config
move nginx\conf.d\default.conf nginx\conf.d\default-ssl.conf

REM Use temp config
move nginx\conf.d\temp.conf nginx\conf.d\default.conf

echo Starting services...
docker-compose up -d

echo Waiting for services to start...
timeout /t 10

echo Obtaining SSL certificate...
echo IMPORTANT: Replace 'your-email@example.com' with your actual email address!

docker run --rm -v %cd%\nginx\certbot\conf:/etc/letsencrypt -v %cd%\nginx\certbot\www:/var/www/certbot certbot/certbot certonly --webroot --webroot-path=/var/www/certbot --email your-email@example.com --agree-tos --no-eff-email -d mlcoe.live

REM Check if certificate was obtained successfully
if exist "nginx\certbot\conf\live\mlcoe.live\fullchain.pem" (
    echo Certificate obtained successfully!
    
    REM Restore SSL configuration
    move nginx\conf.d\default.conf nginx\conf.d\temp.conf
    move nginx\conf.d\default-ssl.conf nginx\conf.d\default.conf
    
    REM Restart nginx with SSL configuration
    docker-compose restart nginx
    
    echo SSL setup complete! Your site should now be accessible at https://mlcoe.live
) else (
    echo Failed to obtain certificate. Please check the logs and try again.
    pause
    exit /b 1
)

echo SSL setup complete!
echo - Your site is now available at https://mlcoe.live
echo - Automatic HTTP to HTTPS redirect is enabled
echo - To renew certificates, run: docker run --rm -v %cd%\nginx\certbot\conf:/etc/letsencrypt -v %cd%\nginx\certbot\www:/var/www/certbot certbot/certbot renew

pause
