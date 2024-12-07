import os
from tempfile import NamedTemporaryFile
import qrcode
import pandas as pd
from django.shortcuts import render
from .forms import PasteDataForm, QRCodeForm, ExcelUploadForm
from io import BytesIO
import base64
from django.http import HttpResponse
from fpdf import FPDF

def generate_qr(request):
    qr_image_base64 = None
    if request.method == 'POST':
        form = QRCodeForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
    else:
        form = QRCodeForm()
    return render(request, 'index.html', {'form': form, 'qr_image_base64': qr_image_base64})

def generate_qrs_from_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        paste_form = PasteDataForm(request.POST)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_excel(file)
        elif paste_form.is_valid():
            data = paste_form.cleaned_data['data']
            rows = data.split('\n')
            df = pd.DataFrame(rows, columns=['Data'])
        else:
            form = ExcelUploadForm()
            paste_form = PasteDataForm()
            return render(request, 'upload.html', {'form': form, 'paste_form': paste_form})

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        qr_per_page = 4
        qr_count = 0
        
        for index, row in df.iterrows():
            if qr_count % qr_per_page == 0:
                pdf.add_page()
            
            data = row.iloc[0]  # Use iloc to access by position
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            
            x = 10 + (qr_count % 2) * 100
            y = 10 + (qr_count // 2 % 2) * 100
            
            buffer.seek(0)
            with NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(buffer.getvalue())
                tmp_file.flush()
                tmp_file_name = tmp_file.name
            
            pdf.image(tmp_file_name, x=x, y=y, w=90, h=90)
            os.unlink(tmp_file_name)
            
            pdf.set_xy(x, y + 95)
            pdf.set_font("Arial", size=12)
            pdf.cell(90, 10, f"QR {index + 1}", ln=True)
            
            qr_count += 1
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="QR_Codes.pdf"'
        pdf_output = pdf.output(dest='S').encode('latin1')
        response.write(pdf_output)
        return response
    else:
        form = ExcelUploadForm()
        paste_form = PasteDataForm()
    return render(request, 'upload.html', {'form': form, 'paste_form': paste_form})

def download_template(request):
    df = pd.DataFrame(columns=['Data'])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="qr_template.xlsx"'
    df.to_excel(response, index=False)
    return response