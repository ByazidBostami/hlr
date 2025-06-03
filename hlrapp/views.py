import re
import time
import csv
import io
import logging
from django import forms
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
import requests

logger = logging.getLogger(__name__)

def clean_number(number):
    """Remove all non-digit characters from the phone number."""
    return re.sub(r'\D', '', number)

def batch_list(lst, n=30):
    """Yield successive n-sized chunks from the list."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def call_hlr_api(msisdn_list):
    url = 'https://api.1s2u.io/hlr'
    numbers = ",".join(msisdn_list)
    data = {
        'username': settings.HLR_USERNAME,
        'password': settings.HLR_PASSWORD,
        'msisdn': numbers,
    }
    try:
        response = requests.post(url, data=data, timeout=15)
        if response.status_code == 200:
            try:
                return response.json(), None
            except ValueError:
                logger.error(f"Invalid JSON response: {response.text}")
                return None, "Received invalid JSON from HLR API"
        elif response.status_code == 429:
            return None, "Rate limit exceeded, please wait and try again."
        else:
            logger.error(f"HLR API error {response.status_code}: {response.text}")
            return None, f"API error: HTTP {response.status_code}"
    except Exception as e:
        logger.error(f"HLR API call failed: {e}")
        return None, f"Request failed: {e}"

# @login_required
# def hlr_lookup(request):
#     result = {}
#     error = None

#     if request.method == 'POST':
#         msisdn_input = request.POST.get('msisdn', '').strip()
#         if msisdn_input:
#             raw_numbers = [line.strip() for line in msisdn_input.split() if line.strip()]
#             msisdn_list = [clean_number(num) for num in raw_numbers if clean_number(num)]

#             if not msisdn_list:
#                 error = "Please enter one or more valid phone numbers."
#             elif len(msisdn_list) > 2000:
#                 error = "You can check up to 2000 numbers at a time."
#             else:
#                 for chunk in batch_list(msisdn_list, 30):
#                     batch_result, batch_error = call_hlr_api(chunk)
#                     if batch_error:
#                         error = batch_error
#                         break
#                     result.update(batch_result or {})
#                     time.sleep(0.04)
#                 if result:
#                     request.session['lookup_result'] = result
#                     request.session.modified = True
#         else:
#             error = "Please enter phone numbers."

#     return render(request, 'hlr_lookup.html', {'result': result, 'error': error})
import time
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def batch_list(lst, n=30):
    """Yield successive n-sized chunks from the list."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
import time
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def batch_list(lst, n=30):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
@login_required
def hlr_lookup(request):
    result = {}
    error = None

    if request.method == 'POST':
        raw_input = request.POST.get('msisdn', '').strip()
        if raw_input:
            numbers = [num.strip() for num in raw_input.split() if num.strip()]
            msisdn_list = [clean_number(n) for n in numbers if clean_number(n)]

            if len(msisdn_list) > 5010:
                error = "Max 5010 numbers allowed."
            elif not msisdn_list:
                error = "Please enter valid phone numbers."
            else:
                for chunk in batch_list(msisdn_list, 28):
                    batch_result, batch_error = call_hlr_api(chunk)
                    if batch_error:
                        error = batch_error
                        break
                    result.update(batch_result or {})
                    time.sleep(0.04)

                if result:
                    request.session['lookup_result'] = result
                    request.session.modified = True
        else:
            error = "Please enter phone numbers."

    return render(request, 'hlr_lookup.html', {'result': result, 'error': error})


# Make sure you have `clean_number` and `call_hlr_api` functions defined as before.

class CSVUploadForm(forms.Form):
    file = forms.FileField(label="Upload CSV file with phone numbers")

@login_required
def upload_csv(request):
    form = CSVUploadForm()
    result = {}
    error = None

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = form.cleaned_data['file']
                data = file.read().decode('utf-8')
                csv_reader = csv.reader(io.StringIO(data))
                numbers = []
                for row in csv_reader:
                    for cell in row:
                        cell_numbers = [clean_number(num) for num in cell.replace(" ", ",").split(",") if clean_number(num)]
                        numbers.extend(cell_numbers)
                numbers = list(set(numbers))
                if not numbers:
                    error = "No valid phone numbers found."
                elif len(numbers) > 2000:
                    error = "Maximum 2000 numbers allowed per request."
                else:
                    for chunk in batch_list(numbers, 30):
                        batch_result, batch_error = call_hlr_api(chunk)
                        if batch_error:
                            error = batch_error
                            break
                        result.update(batch_result or {})
                        time.sleep(0.04)
                    if result:
                        request.session['lookup_result'] = result
                        request.session.modified = True
            except Exception as e:
                error = f"Failed to process file: {e}"

    return render(request, 'upload_csv.html', {'form': form, 'result': result, 'error': error})

@login_required
def download_csv(request):
    result = request.session.get('lookup_result')
    if not result:
        return HttpResponse("No lookup result to download.", status=404)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hlr_lookup_result.csv"'

    writer = csv.writer(response)
    header = ['MSISDN', 'Country', 'Status', 'Error Description', 'Operator', 'Type', 'MCCMNC', 'Roaming', 'Ported']
    writer.writerow(header)

    for val in result.values():
        writer.writerow([
            val.get('msisdn', ''),
            val.get('country', ''),
            val.get('status', ''),
            val.get('err_desc', ''),
            val.get('operator', ''),
            val.get('type', ''),
            val.get('mccmnc', ''),
            val.get('roaming', ''),
            val.get('ported', ''),
        ])

    return response

@login_required
def download_txt(request):
    result = request.session.get('lookup_result')
    if not result:
        return HttpResponse("No lookup result to download.", status=404)

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="hlr_lookup_result.txt"'

    widths = [15, 20, 12, 20, 20, 10, 10, 8, 8]
    headers = ['MSISDN', 'Country', 'Status', 'ErrorDesc', 'Operator', 'Type', 'MCCMNC', 'Roaming', 'Ported']

    def format_row(row):
        return "".join(f"{str(item)[:w]:{w}}" for item, w in zip(row, widths))

    response.write(format_row(headers) + "\n")
    response.write("-" * sum(widths) + "\n")

    for val in result.values():
        row = [
            val.get('msisdn', ''),
            val.get('country', ''),
            val.get('status', ''),
            val.get('err_desc', ''),
            val.get('operator', ''),
            val.get('type', ''),
            val.get('mccmnc', ''),
            val.get('roaming', ''),
            val.get('ported', ''),
        ]
        response.write(format_row(row) + "\n")

    return response
