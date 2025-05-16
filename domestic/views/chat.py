from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

def BgsChatEmbedView(request):
    return render(request, 'domestic/chat.html')