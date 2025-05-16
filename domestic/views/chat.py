from django.shortcuts import render


def bgs_chat_embed(request):
    return render(request, 'domestic/chat.html')
