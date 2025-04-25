@echo off
echo Making migrations...
py manage.py makemigrations

echo Applying migrations...
py manage.py migrate

echo Migrations completed successfully!
pause
