import os
import sys
import subprocess
import platform
from flask import Flask, render_template, jsonify, send_file, request, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'invoice-processor-secret-key-12345'
EXCEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'facturas.xlsx')

@app.route('/open-excel')
def open_excel():
    if os.path.exists(EXCEL_FILE):
        if platform.system() == 'Windows':
            os.startfile(EXCEL_FILE)
        elif platform.system() == 'Darwin': # macOS
            subprocess.run(['open', EXCEL_FILE])
        else: # Linux (Probablemente Render/Nube)
            return jsonify({"success": False, "message": "No se puede abrir Excel en el servidor de la nube. Por favor, descárgalo."}), 400
        return jsonify({"success": True, "message": "Abriendo Excel..."})
    return jsonify({"success": False, "message": "Archivo no encontrado"}), 404

@app.route('/download')
def download():
    if os.path.exists(EXCEL_FILE):
        return send_file(EXCEL_FILE, as_attachment=True)
    return "Archivo no encontrado", 404

@app.route('/download-manual')
def download_manual():
    manual_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MANUAL_USUARIO.txt')
    if os.path.exists(manual_path):
        return send_file(manual_path, as_attachment=True)
    return "Manual no encontrado", 404

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NO_PROCESADOS_DIR = os.path.join(BASE_DIR, 'NO PROCESADOS')
PROCESADOS_DIR = os.path.join(BASE_DIR, 'PROCESADOS')
# Agregar el directorio de la skill al path para poder importarla
SKILL_DIR = os.path.join(BASE_DIR, 'SKILLS', 'InvoiceProcessor', 'scripts')
sys.path.append(SKILL_DIR)
import process_invoices

def count_files(directory):
    if not os.path.exists(directory):
        return 0
    # Contar imágenes comunes
    valid_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')
    return len([f for f in os.listdir(directory) if f.lower().endswith(valid_exts)])

@app.route('/')
def index():
    # Resetear contadores al cargar la página (según requerimiento)
    session['pending'] = 0
    session['processed'] = 0
    return render_template('index.html')

@app.route('/status')
def status():
    # Debug para confirmar ruta
    print(f"DEBUG: Revisando PENDIENTES en {NO_PROCESADOS_DIR}")
    return jsonify({
        'no_procesados': session.get('pending', 0),
        'procesados': session.get('processed', 0)
    })

@app.route('/process', methods=['POST'])
def process():
    try:
        # Ejecutar la skill (procesa nuevos y actualiza Excel)
        newly_processed, failed_files = process_invoices.main()
        
        # Actualizar contadores de sesión
        count = len(newly_processed)
        session['processed'] = session.get('processed', 0) + count
        
        # Llevar a 0 el pendiente (Quitar de memoria las no procesadas)
        session['pending'] = 0
        
        # Obtener los registros actualizados (lista simple ordenada por vencimiento)
        all_records = process_invoices.get_grouped_records()
        
        # Construir mensaje de respuesta con aviso de fallos si existen
        message = f'Se procesaron {len(newly_processed)} facturas con éxito.'
        if failed_files:
            message += f" [AVISO: {len(failed_files)} no se procesaron: {', '.join(failed_files)}]"
        
        return jsonify({
            'success': True,
            'message': message,
            'data': all_records 
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error al procesar las facturas.',
            'error': str(e)
        }), 500

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({"success": False, "message": "No se enviaron archivos"}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({"success": False, "message": "No se seleccionaron archivos"}), 400

    count = 0
    os.makedirs(NO_PROCESADOS_DIR, exist_ok=True)
    
    for file in files:
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filename = secure_filename(file.filename)
            file.save(os.path.join(NO_PROCESADOS_DIR, filename))
            count += 1
            
    session['pending'] = session.get('pending', 0) + count
            
    return jsonify({
        "success": True, 
        "message": f"Se subieron {count} archivos exitosamente.",
        "count": count
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
