from django.shortcuts import render
import generator.poemeGenerator as poemeGenerator
from generator.forms import QuizForm
import threading

# Create your views here.

def home(request):
    forme = ""
    sylla = ""
    phone = ""

    if request.method == 'POST':
        # créer une instance de notre formulaire et le remplir avec les données POST
        form = QuizForm(request.POST)

        if form.is_valid():
            forme = request.POST.get('forme')
            sylla = request.POST.get('sylla')
            phone = request.POST.get('phone')

        # prev = poemeGenerator.prev(forme, sylla, phone)[0].split("\n")

        poem, err1, err2 = poemeGenerator.main(forme, sylla, phone)
        print(poem)

        return render(request, 'generator/home.html',
                      {'form': form, 'poem': poem, 'err1': err1, 'err2': err2})  # ajoutez cette instruction de retour

        # si le formulaire n'est pas valide, nous laissons l'exécution continuer jusqu'au return
        # ci-dessous et afficher à nouveau le formulaire (avec des erreurs).

    else:
        # ceci doit être une requête GET, donc créer un formulaire vide
        form = QuizForm()

    return render(request,
                  'generator/home.html',
                  {'form': form})


def aide(request):
    aidephon = poemeGenerator.aidephon
    return render(request, 'generator/aide.html', {'aidephon': aidephon})

def app(request):
    return render(request, 'generator/app.html')