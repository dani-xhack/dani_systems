from django.shortcuts import render, redirect
from web.models import Joke

def teleport_index(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'joke')
        name = request.POST.get('name', '').strip()
        text = request.POST.get('text', '').strip()

        if name and text:
            if form_type == 'hex':
                Joke.objects.create(name=name, text='[HEX]' + text, is_published=False)
                return redirect('/teleport/?hex_sent=1#hex-jokes')
            else:
                Joke.objects.create(name=name, text=text, is_published=False)
                return redirect('/teleport/?joke_sent=1#jokes')

    all_published = Joke.objects.filter(is_published=True).order_by('-created_at')
    jokes = [j for j in all_published if not j.text.startswith('[HEX]')]
    hex_jokes = [
        {'id': j.id, 'name': j.name, 'hex': j.text[5:], 'created_at': j.created_at}
        for j in all_published if j.text.startswith('[HEX]')
    ]

    return render(request, 'teleport/index.html', {
        'jokes': jokes,
        'hex_jokes': hex_jokes,
    })

