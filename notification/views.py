from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'notification/index.html', {})


def chat(request, room_name):
    context = {
        'room_name': room_name
    }
    return render(request, 'notification/room.html', context)