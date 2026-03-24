from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Factura, UserProfile
from .services import procesar_factura_ia
from django.core.files.storage import default_storage
import json
import os
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, Alignment
from io import BytesIO
from django.http import HttpResponse, FileResponse

@login_required
def dashboard_view(request):
    facturas = Factura.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'scanner/dashboard.html', {'facturas': facturas})

@login_required
def config_view(request):
    perfil, created = UserProfile.objects.get_or_create(usuario=request.user)
    if request.method == 'POST':
        api_key = request.POST.get('api_key')
        perfil.gemini_api_key = api_key
        perfil.save()
        return redirect('scanner:dashboard')
    return render(request, 'scanner/config.html', {'perfil': perfil})

@csrf_exempt
@login_required
def upload_invoices_view(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        perfil, _ = UserProfile.objects.get_or_create(usuario=request.user)
        user_key = perfil.gemini_api_key
        
        results = []
        for f in files:
            temp_path = default_storage.save(f'temp_facturas/{f.name}', f)
            full_path = default_storage.path(temp_path)
            
            data = procesar_factura_ia(full_path, user_api_key=user_key)
            if data:
                data['temp_file'] = temp_path
                results.append(data)
            else:
                results.append({
                    'suplidor': 'Error IA',
                    'fecha_emision_display': datetime.today().strftime('%d/%m/%Y'),
                    'fecha_vencimiento_display': (datetime.today()).strftime('%d/%m/%Y'),
                    'temp_file': temp_path
                })
        return JsonResponse({'success': True, 'data': results})
    return render(request, 'scanner/upload.html')

@csrf_exempt
@login_required
def export_excel_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Reporte Facturas RD"
            
            headers = ["Suplidor", "Fecha", "Fecha Vence", "Factura No.", "NCF", "ITBIS", "Total", "RNC"]
            ws.append(headers)
            
            for item in data:
                ws.append([
                    item.get('suplidor'),
                    item.get('fecha_emision_display'),
                    item.get('fecha_vencimiento_display'),
                    item.get('num_factura'),
                    item.get('ncf'),
                    float(item.get('itbis', 0).replace(',', '') if isinstance(item.get('itbis'), str) else item.get('itbis', 0)),
                    float(item.get('total', 0).replace(',', '') if isinstance(item.get('total'), str) else item.get('total', 0)),
                    item.get('rnc_suplidor')
                ])
            
            for col in ws.columns:
                max_length = 0
                for cell in col:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                ws.column_dimensions[col[0].column_letter].width = max_length + 2
            
            filename = f"Reporte_InvoicePro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            if os.name == 'nt':
                # Local Windows behavior: save and open
                filepath = os.path.join(os.getcwd(), filename)
                wb.save(filepath)
                os.startfile(filepath)
                return JsonResponse({'success': True})
            else:
                # Production/Linux behavior: binary download
                output = BytesIO()
                wb.save(output)
                output.seek(0)
                response = HttpResponse(
                    output.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    return JsonResponse({'success': False})

@csrf_exempt
@login_required
def save_confirmed_invoices_view(request):
    if request.method == 'POST':
        try:
            data_list = json.loads(request.body)
            for item in data_list:
                # REFUERZO: Mapeo explícito y validado de num_factura
                factura = Factura(
                    usuario=request.user,
                    suplidor=item.get('suplidor'),
                    rnc_suplidor=item.get('rnc_suplidor'),
                    num_factura=item.get('num_factura') or "S/N", # Aseguramos persistencia
                    ncf=item.get('ncf'),
                    fecha_emision=item.get('fecha_emision'),
                    vencimiento_factura=item.get('fecha_vencimiento'),
                    itbis=item.get('itbis') or 0,
                    total=item.get('total') or 0,
                    archivo_original=item.get('temp_file'),
                    procesada=True
                )
                factura.save()
            return JsonResponse({'success': True})
        except Exception as e:
            print(f"Error Guardando: {e}")
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False})

@login_required
def delete_invoice_view(request, pk):
    factura = get_object_or_404(Factura, usuario=request.user, pk=pk)
    factura.delete()
    return redirect('scanner:dashboard')
