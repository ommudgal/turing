@echo off
echo Testing Rate Limiting Implementation
echo =====================================

echo.
echo 1. Testing Registration Endpoint (3 requests per minute limit)
echo ----------------------------------------------------------------
for /L %%i in (1,1,5) do (
    echo Request %%i:
    curl -s -w "Status: %%{http_code}\n" -X POST "https://mlcoe.live/api/v1/student/register" ^
        -H "Content-Type: application/json" ^
        -d "{\"firstName\":\"Test%%i\",\"lastName\":\"User\",\"email\":\"test%%i@example.com\",\"phoneNumber\":\"1234567890\",\"state\":\"TestState\",\"city\":\"TestCity\",\"pincode\":\"123456\",\"college\":\"TestCollege\",\"course\":\"TestCourse\",\"year\":\"1\"}" ^
        -o nul
    timeout /t 1 >nul
)

echo.
echo 2. Testing Verification Endpoint (10 requests per minute limit)
echo ----------------------------------------------------------------
for /L %%i in (1,1,12) do (
    echo Request %%i:
    curl -s -w "Status: %%{http_code}\n" -X POST "https://mlcoe.live/api/v1/student/verify" ^
        -H "Content-Type: application/json" ^
        -d "{\"email\":\"test@example.com\",\"otp\":\"123456\"}" ^
        -o nul
    timeout /t 1 >nul
)

echo.
echo 3. Testing Resend OTP Endpoint (1 request per 2 minutes limit)
echo ----------------------------------------------------------------
for /L %%i in (1,1,3) do (
    echo Request %%i:
    curl -s -w "Status: %%{http_code}\n" -X GET "https://mlcoe.live/api/v1/student/resend-otp?email=test@example.com" ^
        -o nul
    timeout /t 1 >nul
)

echo.
echo 4. Testing Captcha Validation Endpoint (5 requests per minute limit)
echo ---------------------------------------------------------------------
for /L %%i in (1,1,7) do (
    echo Request %%i:
    curl -s -w "Status: %%{http_code}\n" -X POST "https://mlcoe.live/api/v1/student/validate" ^
        -H "Content-Type: application/json" ^
        -d "{\"token\":\"test-token-%%i\"}" ^
        -o nul
    timeout /t 1 >nul
)

echo.
echo 5. Testing General API Rate Limit (30 requests per minute for /api/)
echo ---------------------------------------------------------------------
for /L %%i in (1,1,35) do (
    echo Request %%i:
    curl -s -w "Status: %%{http_code}\n" -X GET "https://mlcoe.live/api/v1/student/resend-otp?email=test@example.com" ^
        -o nul
    if %%i GTR 30 (
        echo Expected: 429 Too Many Requests
    )
    timeout /t 1 >nul
)

echo.
echo Rate Limiting Test Complete!
echo.
echo Expected Results:
echo - Registration: First 3 requests should be 200/400, 4th and 5th should be 429
echo - Verification: First 10 requests should be 200/400, 11th and 12th should be 429  
echo - Resend OTP: First request should be 200/400, 2nd and 3rd should be 429
echo - Captcha: First 5 requests should be 200/400, 6th and 7th should be 429
echo - General API: First 30 requests should be 200/400, 31st+ should be 429
echo.
echo 429 = Rate limit exceeded (this is what we want to see!)
echo 200/400 = Normal API response (depending on valid/invalid data)
pause
