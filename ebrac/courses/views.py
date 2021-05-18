from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from .models import Course,Module,Content,Subject,Question,Quiz,Answer,Result
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet,QuestionFormSet
from django.forms.models import modelform_factory
from django.apps import apps
from django.db.models import Count
from students.forms import CourseEnrollForm
from django.shortcuts import render
from django.http import JsonResponse


class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class OwnerCourseMixin(OwnerMixin,LoginRequiredMixin,PermissionRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')

class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'

class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'

class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'

class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'
    
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'
    
class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None
    
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,
                             data=data)
    
    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super().dispatch(request, pk)
    
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                        'formset': formset})
    
    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course,
                                        'formset': formset})
    
class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file','quiz']:
            return apps.get_model(app_label='courses',
                                  model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                'order',
                                'created',
                                'updated'])
        return Form(*args, **kwargs)
    

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)
        self.model = self.get_model(model_name)
        
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        return super().dispatch(request, module_id, model_name, id)
    
    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
        'object': self.obj})
    
    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            
            if not id:
                # new content
                Content.objects.create(module=self.module,
                item=obj)
            if model_name == 'quiz':
                return redirect('quiz_question_create',module_id=self.module.id,quiz_id=obj.id)
                                
            return redirect('module_content_list', self.module.id)
            
        return self.render_to_response({'form': form,
                'object': self.obj})

    
    
    
class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)
    
class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'
    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)
        return self.render_to_response({'module': module})
    

class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'
    
    def get(self, request, subject=None):
        subjects = Subject.objects.annotate(total_courses=Count('courses'))
        courses = Course.objects.annotate(total_modules=Count('modules'))
        
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject)
        return self.render_to_response({'subjects': subjects,
            'subject': subject,
            'courses': courses})
    
class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(initial={'course':self.object})
        return context
    
class QuestionCreateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/content/question.html'
    module = None
    model = None
    obj = None
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, fields=['text',])
        return Form(*args, **kwargs)
    
    def dispatch(self, request, module_id, quiz_id, id=None):
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)
        self.model = Question
        self.quiz = get_object_or_404(Quiz,
                                        id=quiz_id,
                                        owner=request.user)
        
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         quiz__owner=request.user)
        return super().dispatch(request, module_id, quiz_id, id)
        
    def get(self, request, module_id, quiz_id,id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
        'object': self.obj})
    
    def post(self, request, module_id, quiz_id,id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.quiz = self.quiz
            obj.save()
            
                                
            return redirect('question_answer_add', self.module.id,self.quiz.id,obj.id)
            
        return self.render_to_response({'form': form,
                'object': self.obj})
    

class AnswerAddView(TemplateResponseMixin, View):
    template_name = 'courses/manage/content/answers.html'
    question = None
    
    def get_formset(self, data=None):
        return QuestionFormSet(instance=self.question,
                             data=data)
    
    def dispatch(self, request, module_id, quiz_id, id):
        self.quiz = get_object_or_404(Quiz,
                                        id=quiz_id,
                                        owner=request.user)
        self.question = get_object_or_404(Question,
                                        id=id,
                                        quiz=self.quiz)
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)
        return super().dispatch(request,  module_id, quiz_id, id)
    
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'question': self.question,
                                        'formset': formset})
    
    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            if len(self.quiz.questions.all())<self.quiz.number_of_questions:
                return redirect('quiz_question_create',module_id=self.module.id,quiz_id=self.quiz.id)
            return redirect('module_content_list',self.module.id)
        return self.render_to_response({'question': self.question,
                                        'formset': formset})


    
def quiz_view(request,course_id,module_id,pk):
    quiz = Quiz.objects.get(pk=pk)
    if quiz.ended:
        questions = []
        for q in quiz.get_questions():
            answers=[]
            for a in q.get_answers():
                if a.correct:
                    answers.append(a.text)
            questions.append({str(q):answers})
        return render(request,'courses/content/quiz/quiz_ended.html',
                      {'obj':quiz,'result':quiz.quiz_result.get(user=request.user),'questions':questions})
    
    if quiz.quiz_result.filter(user=request.user):
        return render(request,'courses/content/quiz/quiz_completed.html',
                      {'obj':quiz.quiz_result.get(user=request.user),'course_id':course_id})
    
    return render(request,'courses/content/quiz/quiz.html',{'obj':quiz})

def quiz_data_view(request,course_id,module_id,pk):
    quiz = Quiz.objects.get(pk=pk)
    questions = []
    for q in quiz.get_questions():
        answers=[]
        for a in q.get_answers():
            answers.append(a.text)
        questions.append({str(q):answers})
    
    return JsonResponse({'data':questions,'time':quiz.time})

def save_quiz_view(request,course_id,module_id,pk):
    quiz = Quiz.objects.get(pk=pk)
    # m= quiz.content.all()[0].module
    if request.is_ajax():
        questions = []
        data=request.POST
        data_ = dict(data.lists())
        print(data_)
        data_.pop('csrfmiddlewaretoken')
        
        for k in data_.keys():
            print('key : ',k)
            question = quiz.questions.filter(text=k)[0]
            print(question)
            questions.append(question)
        print(questions)
        
        user = request.user
        quiz = Quiz.objects.get(pk=pk)
        
        score = 0
        multiplier = 100/quiz.number_of_questions
        results = []
        correct_answer = None
        
        for q in questions:
            a_selected = request.POST.get(q.text)
            # print('selected : ',a_selected)
            
            if a_selected !="":
                question_answers = Answer.objects.filter(question=q)
                for a in question_answers:
                    if a_selected == a.text:
                        if a.correct:
                            score +=1
                            correct_answer = a.text
                
                    else:
                        if a.correct:
                             correct_answer = a.text
                             
                results.append({str(q):{'correct_answer' : correct_answer,
                                        'answered':a_selected}})
                
            else:
                results.append({str(q):'not answered'})
           
        score_ = score*multiplier
        Result.objects.create(quiz=quiz,user=user,score=score_)

        if score_>=quiz.required_score_to_pass:
            return JsonResponse({'passed':True,'score':f'{score_:.2f}','results':results})                    
        
        else:
            
            return JsonResponse({'passed':False,'score':f'{score_:.2f}','results':results})                    
    

class ResultListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    
    template_name = 'courses/manage/quiz/result.html'
    context_object_name = 'course_list'
    permission_required = 'courses.view_course' 
    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user)
  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = {}
        averages={}
        for c in context['course_list']:
            student=c.students.all()
            for s in student:
                res= Result.objects.filter(user=s)
                for r in res:
                    m = r.quiz.content.all()[0].module
                    c = m.course
                    if c in results:
                        if s in results[c]:
                            if m in results[c][s]:
                                if r not in results[c][s][m]: 
                                    results[c][s][m].append(r)
                                    averages[c][s].append(r.score)
                            else:
                                results[c][s][m]=[r]
                                averages[c][s]=[r.score]
                        else:
                            results[c][s] = {m:[r]}
                            averages[c][s] = [r.score]
                    else:
                        results[c] = {s :{m :[r]}}
                        averages[c] = {s :[r.score]}
                averages[c][s]= list(averages[c][s])
                sum = 0
                count = 0
                for x in averages[c][s]:
                    sum = sum + x
                    count = count + 1
                averages[c][s] = [sum / count]
                results[c][s]['averages'] = averages[c][s]
        context['student_results'] = results
        
        return context        