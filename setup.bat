@echo off

echo ==========================================
echo bale2bale Windows Setup
echo ==========================================
echo.

echo Installing requirements...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Failed to install requirements.
    pause
    exit /b
)

echo.
set /p BOT_TOKEN=Enter your Bale bot token: 
set /p CHNL_UID=Enter Bale destination channel/group UID: 
set /p DATAS_UID=Enter Bale forwarding channel/group UID: 

echo.
echo Enter channels in this format:
echo channel_username:limit
echo Example:
echo bbcpersian:5
echo.

(
echo BOT_TOKEN = "%BOT_TOKEN%"
echo CHNL_UID = %CHNL_UID%
echo DATAS_UID = %DATAS_UID%
echo.
echo CHANNELS = {
) > config.py

:loop
set /p CHANNEL=Channel ^(Press ENTER to finish^): 

if "%CHANNEL%"=="" goto done

for /f "tokens=1,2 delims=:" %%a in ("%CHANNEL%") do (
    echo     "%%a": %%b, >> config.py
)

goto loop

:done

echo } >> config.py

echo.
echo Setup completed successfully.
echo Run the bot using:
echo python main.py
echo.

pause
