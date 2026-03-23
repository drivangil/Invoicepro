import google.generativeai as genai
import json
import os
import time
from .models import Factura
from PIL import Image
from django.conf import settings
from datetime import datetime, timedelta

SYSTEM_PROMPT = """
Actúa como un experto fiscal de República Dominicana. Extrae datos fiscales de facturas de República Dominicana.
Devuelve únicamente un JSON estricto con los siguientes campos:
1. suplidor (Nombre del negocio)
2. rnc_suplidor (9 u 11 dígitos, sin guiones)
3. num_factura (Número interno de factura)
4. ncf (Comprobante Fiscal: B01, B02, E31, E32, B14, B15, etc. Debe ser de 11 o 13 caracteres)
5. fecha_emision (Formato YYYY-MM-DD)
6. fecha_vencimiento (Formato YYYY-MM-DD. Si no se indica, devuelve null)
7. itbis (Decimal con punto)
8. total (Decimal con punto)

Reglas Críticas:
- NCF es mandatory (11 o 13 chars).
- Respuesta en JSON puro.
"""

def procesar_factura_ia(file_path, user_api_key=None, max_retries=3):
    api_key = user_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    genai.configure(api_key=api_key)
    
    # Motor de última generación 2026 (Fix: Prefijo models/ obligatorio)
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    for attempt in range(max_retries):
        try:
            with Image.open(file_path) as img:
                img_rgb = img.convert('RGB')
                response = model.generate_content([SYSTEM_PROMPT, img_rgb])
                
                text_response = response.text.replace('```json', '').replace('```', '').strip()
                data = json.loads(text_response)
                
                if data.get('fecha_emision'):
                    emision = datetime.strptime(data['fecha_emision'], '%Y-%m-%d')
                    if not data.get('fecha_vencimiento'):
                        vence = emision + timedelta(days=30)
                        data['fecha_vencimiento'] = vence.strftime('%Y-%m-%d')
                    
                    data['fecha_emision_display'] = datetime.strptime(data['fecha_emision'], '%Y-%m-%d').strftime('%d/%m/%Y')
                    data['fecha_vencimiento_display'] = datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').strftime('%d/%m/%Y')
                
                return data
                
        except Exception as e:
            print(f"DEBUG: Intento {attempt + 1}/{max_retries} fallido para {os.path.basename(file_path)}: {str(e)}")
            time.sleep(3)
                
    return None
