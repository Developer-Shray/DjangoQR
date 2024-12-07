from django import forms

class QRCodeForm(forms.Form):
    text = forms.CharField(label='Paste the URL', max_length=255)

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label='Upload Excel File')

class PasteDataForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea, label='Paste Data Here')