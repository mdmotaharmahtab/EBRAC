# ebrac
This is an online learning platform created by django framework. There are two types of users - students and teachers. Teachers can create courses, add different course contents - text, video, image etc. They can create quizzes, see students' marksheet, see enrolled students in a course, their created courses etc. Students can view course content, enroll in a course, take a quiz, see their marksheet etc. 

## <a href='https://youtu.be/NKG48BIQugQ'>Project Demo Video</a>
![Alt text](https://github.com/MotaharMahtab/ebrac/blob/master/Functionalities.gif)
In order to start the django projec, do the following :

## Running this project

To get this project up and running you should start by having Python installed on your computer. It's advised you create a virtual environment to store your projects dependencies separately. You can install virtualenv with

```
pip install virtualenv
```

Clone or download this repository and open it in your editor of choice. In a terminal (mac/linux) or windows terminal, run the following command in the base directory of this project

```
virtualenv envname
```

That will create a new folder `env` in your project directory. Next activate it with this command on mac/linux:

```
.\envname\Scripts\activate
```

Then install the project dependencies with

```
pip install -r requirements.txt
```
Then cd into the project directory
```
cd ebrac
```
Now you can run the project with this command

```
python manage.py runserver
```
