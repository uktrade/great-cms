from django import forms


from learn.models import Lesson

class LessonForm(forms.ModelForm):

    class Meta:
        model = Lesson
        fields = '__all__'