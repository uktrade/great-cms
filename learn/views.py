from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.middleware.csrf import get_token
from django_common.http import JsonResponse
from learn.models import Lesson
from learn.forms import LessonForm


def lesson_list(request, template='lesson/list.html'):
    d = {}
    d['form'] = LessonForm()
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            item = form.save()
            return JsonResponse(data={'id': item.id, 'name': str(item), 'form': LessonForm().as_p(), 'token': get_token(request)})
        else:
            d['form'] = form
            return JsonResponse(data={'form': d['form'].as_p(), 'token': get_token(request)}, success=False)
    d['lesson_list'] = Lesson.objects.all()
    return render(request, template, d)


def lesson_details(request, id, template='lesson/details.html'):
    d = {}
    item = get_object_or_404(Lesson, pk=id)
    d['form'] = LessonForm(instance=item)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            return JsonResponse(data={'form': LessonForm(instance=item).as_p(), 'token': get_token(request)})
        else:
            d['form'] = form
            return JsonResponse(data={'form': d['form'].as_p(), 'token': get_token(request)}, success=False)
    d['lesson'] = Lesson.objects.get(pk=id)
    return render(request, template, d)


def lesson_delete(request, id):
    item = Lesson.objects.get(pk=id)
    item.delete()
    return JsonResponse()
