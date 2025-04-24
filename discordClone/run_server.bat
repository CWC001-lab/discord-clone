@echo off
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
