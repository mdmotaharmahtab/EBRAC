# ebrac
This is an online learning platform created by django framework
In order to start the django projec, do the following :

1. Create a virtual environment in your desired folder and activate it.
2. pip install django, Pillow and django-embed-video
3. Create a new djanog project django-admin startproject ebrac
4. Inside this ebrac folder, create courses and students apps (python manage.py startapp courses)
5. Copy all the files from google drive project in your courses and students folder
6. Copy the urls.py of ebrac from google drive and also change your settings.py just like in the google drive folder
7. Create the database - python manage.py makemigrations and python manage.py migrate
8. Create an admin (python manage.py createsuperuser)
9. Run the server (python manage.py runserver)
