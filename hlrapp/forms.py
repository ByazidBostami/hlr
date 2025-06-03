from django import forms

class CSVUploadForm(forms.Form):
    file = forms.FileField(label="Upload CSV file with phone numbers")
