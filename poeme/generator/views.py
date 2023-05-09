from django.shortcuts import render
import generator.poemeGenerator as poemeGenerator
from generator.forms import QuizForm

# Create your views here.
def home(request):
    if request.method == 'POST':
        # créer une instance de notre formulaire et le remplir avec les données POST
        form = QuizForm(request.POST)

        forme = "ABBA"
        sylla = "1=12"
        phone = ""

        if form.is_valid():
            forme = request.POST.get('forme')
            sylla = request.POST.get('sylla')
            phone = request.POST.get('phone')

        poem = poemeGenerator.main(forme, sylla, phone)
        err1 = poemeGenerator.err1
        err2 = poemeGenerator.err2

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