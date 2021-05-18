from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField
from django.template.loader import render_to_string
from django.contrib.contenttypes.fields import GenericRelation


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    class Meta:
        ordering = ['title']
    def __str__(self):
        return self.title

class Course(models.Model):
    owner = models.ForeignKey(User,
    related_name='courses_created',
    on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,
                                related_name='courses',
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User,
                                      related_name='courses_joined',
                                      blank=True)
    class Meta:
        ordering = ['-created']
    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course,
    related_name='modules',
    on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])
    class Meta:
        ordering = ['order']
    def __str__(self):
        return f'{self.order}. {self.title}'
   
    
class Content(models.Model):
    module = models.ForeignKey(Module,
    related_name='contents',
    on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
    on_delete=models.CASCADE,limit_choices_to={'model__in':('text','video','image',
                                                'file','quiz')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])
    class Meta:
        ordering = ['order']
    
    
    
class ItemBase(models.Model):
    owner = models.ForeignKey(User,
    related_name='%(class)s_related',
    on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
    def __str__(self):
        return self.title
    def render(self):
        return render_to_string(f'courses/content/{self._meta.model_name}.html',{'item': self })
    
class Text(ItemBase):
    content = models.TextField()

class File(ItemBase):
    file = models.FileField(upload_to='files')

class Image(ItemBase):
    file = models.FileField(upload_to='images')

class Video(ItemBase):
    url = models.URLField()

DIFF_CHOICES = (
    ('easy', 'easy'),
    ('medium', 'medium'),
    ('hard', 'hard'),
)
class Quiz(ItemBase): 
    topic = models.CharField(max_length=120)
    number_of_questions = models.IntegerField()
    time = models.FloatField(help_text="duration of the quiz in minutes")
    required_score_to_pass = models.IntegerField(help_text="required score in %")
    difficulty = models.CharField(max_length=6, choices=DIFF_CHOICES)
    content = GenericRelation(Content)
    ended = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title}-{self.topic}"

    def get_questions(self):
        questions = list(self.questions.all())
        return questions
    def render(self):
        return render_to_string('courses/content/quiz/main.html',{'object': self })
    
    class Meta:
        verbose_name_plural = 'Quizes'
        
        
class Question(models.Model):
    text = models.CharField(max_length=200)
    quiz = models.ForeignKey(Quiz,related_name='questions', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.text)

    def get_answers(self):
        return self.answers.all()

class Answer(models.Model):
    text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question,related_name='answers', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"question: {self.question.text}, answer: {self.text}, correct: {self.correct}"
    
class Result(models.Model):
    quiz = models.ForeignKey(Quiz,related_name="quiz_result", on_delete=models.CASCADE)
    user = models.ForeignKey(User,related_name="student_result", on_delete=models.CASCADE)
    score = models.FloatField()

    def __str__(self):
        return str(self.pk)