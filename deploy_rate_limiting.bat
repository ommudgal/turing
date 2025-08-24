@echo off
echo Deploying rate limiting updates to EC2 server...

REM Upload docker-compose configuration
echo Uploading docker-compose configuration...
scp -i yoga.pem docker-compose.yml ubuntu@mlcoe.live:/home/ubuntu/mlcoe/

REM Upload nginx configuration
echo Uploading nginx configuration...
scp -i yoga.pem nginx/conf.d/default.conf ubuntu@mlcoe.live:/home/ubuntu/mlcoe/nginx/conf.d/

REM Upload backend requirements
echo Uploading backend requirements...
scp -i yoga.pem backend/requirements.txt ubuntu@mlcoe.live:/home/ubuntu/mlcoe/backend/

REM Upload backend main.py
echo Uploading backend main.py...
scp -i yoga.pem backend/src/main.py ubuntu@mlcoe.live:/home/ubuntu/mlcoe/backend/src/

REM Upload backend student routes
echo Uploading backend student routes...
scp -i yoga.pem backend/src/routes/student.py ubuntu@mlcoe.live:/home/ubuntu/mlcoe/backend/src/routes/

echo Upload complete! Now rebuilding services...

REM SSH to server and rebuild services
ssh -i yoga.pem ubuntu@mlcoe.live "cd mlcoe && docker-compose down && docker-compose build backend && docker-compose up -d"

echo Deployment complete! Testing rate limiting...

REM Test rate limiting
echo Testing registration endpoint rate limiting (should work first 3 times, then get rate limited)...
for /L %%i in (1,1,5) do (
    echo Request %%i:
    curl -X POST "https://mlcoe.live/api/register" -H "Content-Type: application/json" -d "{\"firstName\":\"Test\",\"lastName\":\"User\",\"email\":\"test%%i@example.com\",\"phoneNumber\":\"1234567890\",\"state\":\"TestState\",\"city\":\"TestCity\",\"pincode\":\"123456\",\"college\":\"TestCollege\",\"course\":\"TestCourse\",\"year\":\"1\"}"
    echo.
    timeout /t 1 >nul
)

echo.
echo Rate limiting deployment complete!
echo Check the logs with: ssh -i yoga.pem ubuntu@mlcoe.live "cd mlcoe && docker-compose logs -f"
pause
