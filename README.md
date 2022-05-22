# ebrac
This is an online learning platform created by django framework. There are two types of users - students and teachers. Teachers can create courses, add different course contents - text, video, image etc. They can create quizzes, see students' marksheet, see enrolled students in a course, their created courses etc. Students can view course content, enroll in a course, take a quiz, see their marksheet etc. 

## <a href='https://youtu.be/NKG48BIQugQ'>Project Demo Video</a>
![Alt text](https://github.com/MotaharMahtab/ebrac/blob/master/Functionalities.gif)
In order to start the django projec, do the following :

1. Create a virtual environment in your desired folder and activate it. 
``` console 
virtualenv -p python3 envname 
.\envname\Scripts\activate 
```
2. Install all the required modules - ``` pip install -r requirements.txt ```
3. Create a new django project ``` django-admin startproject ebrac ```
4. Inside this ebrac folder, create courses and students apps (``` python manage.py startapp courses ```)
5. Copy all the files from google drive project in your courses and students folder
6. Copy the urls.py of ebrac from google drive and also change your settings.py just like in the google drive folder
7. Create the database - ``` python manage.py makemigrations``` and ``` python manage.py migrate```
8. Create an admin (``` python manage.py createsuperuser```)
9. Run the server (``` python manage.py runserver```)
