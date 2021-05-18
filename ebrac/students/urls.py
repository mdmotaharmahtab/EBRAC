# -*- coding: utf-8 -*-
from django.urls import path
from . import views
from courses.views import quiz_view,quiz_data_view,save_quiz_view
urlpatterns = [
                path('register/',
                views.StudentRegistrationView.as_view(),
                name='student_registration'),
                
                path('enroll-course/',
                     views.StudentEnrollCourseView.as_view(),
                     name='student_enroll_course'),
                
                path('courses/',
                     views.StudentCourseListView.as_view(),
                     name='student_course_list'),

                path('course/<pk>/',
                     views.StudentCourseDetailView.as_view(),
                     name='student_course_detail'),

                path('course/<pk>/<module_id>/',
                     views.StudentCourseDetailView.as_view(),
                     name='student_course_detail_module'),
                
                
                path('course/<course_id>/<module_id>/<pk>/',
                     quiz_view,
                     name='student-quiz-start-view'),
                
                path('course/<course_id>/<module_id>/<pk>/data/',
                    quiz_data_view,
                     name='student_quiz-data-view'),
                
                path('course/<course_id>/<module_id>/<pk>/save/',
                     save_quiz_view,
                     name='student_quiz-save-view'),
                
                path('courses/result/',
                     views.StudentQuizResultListView.as_view(),
                     name='student_quiz_results'),
                
]
