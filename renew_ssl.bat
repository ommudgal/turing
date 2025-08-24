@echo off
echo Renewing SSL certificates...

docker run --rm -v %cd%\nginx\certbot\conf:/etc/letsencrypt -v %cd%\nginx\certbot\www:/var/www/certbot certbot/certbot renew --quiet

if %ERRORLEVEL% == 0 (
    echo Certificate renewal successful!
    docker-compose restart nginx
    echo Nginx restarted with renewed certificates.
) else (
    echo Certificate renewal failed. Please check the logs.
)

pause
