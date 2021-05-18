# -*- coding: utf-8 -*-

from django.forms.models import inlineformset_factory
from .models import Course, Module,Question,Answer

ModuleFormSet = inlineformset_factory(Course,Module,fields=['title','description'],extra=2,can_delete=True)
QuestionFormSet = inlineformset_factory(Question,Answer,fields=['text','correct'],extra=4,can_delete=True)