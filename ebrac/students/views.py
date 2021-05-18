from django.urls import reverse_lazy
from django.views.generic.edit import CreateView,FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseEnrollForm
from django.views.generic.list import ListView
from courses.models import Course,Result
from django.views.generic.detail import DetailView

# Create your views here.
class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')

    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password1'])
        login(self.request, user)
        return result
    

class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm
    
    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('student_course_detail',
        args=[self.course.id])
    
    
class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])
    
class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = course.modules.get(
                                    id=self.kwargs['module_id'])
        else:
            # get first module
            if len(course.modules.all())>0:
                context['module'] = course.modules.all()[0]
            else:
                context['module'] = None
            
        return context

class StudentQuizResultListView(LoginRequiredMixin, ListView):
    model = Result
    context_object_name = 'my_results'
    template_name = 'students/quiz/result.html'
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user__in=[self.request.user])
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = {}
        for result in context['my_results']:
            m = result.quiz.content.all()[0].module
            c = m.course
            if c in courses:
                if m in courses[c]:
                    courses[c][m].append(result)
                else:
                    courses[c][m]=[result]
            else:    
                courses[c] = {m:[result]}
        context['courses'] = courses
        return context        