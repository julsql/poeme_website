from django import forms

class QuizForm(forms.Form):
    forme = forms.CharField(
        required=True,
        label='Forme (ABBA ABAB …) :',
        widget=forms.TextInput(attrs={'placeholder': 'forme du poème'})
    )
    sylla = forms.CharField(
        required=False,
        label='Syllabes (1=12, 4=8) :',
        widget=forms.TextInput(attrs={'placeholder': 'nombre de syllabe'})
    )
    phone = forms.CharField(
        required=False,
        label='Phonétique (A=t@t, B=se …) :',
        widget=forms.TextInput(attrs={'placeholder': 'phonétique'})
    )
