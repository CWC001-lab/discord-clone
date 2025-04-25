@echo off
echo Checking database connection...
py check_db_connection.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Database connection failed!
    echo The server will start, but you may encounter database errors.
    echo Please check your database credentials and network connection.
    echo.
    pause
)

echo Applying migrations...
py manage.py makemigrations
py manage.py migrate

echo Do you want to create a superuser? (y/n)
set /p create_superuser=

if /i "%create_superuser%"=="y" (
    echo Creating superuser...
    py manage.py createsuperuser
)

echo Starting server...
py manage.py runserver

pause
