import os
import sys
import subprocess
import platform
import zipfile
import io
from flask import Flask, render_template, jsonify, send_file, request, session, send_from_directory
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

@app.route('/download-file/<filename>')
def download_file(filename):
    """Descarga una factura individual procesada."""
    filepath = os.path.join(PROCESADOS_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "Archivo no encontrado", 404

@app.route('/download-all')
def download_all():
    """Crea un ZIP con el Excel y todas las facturas procesadas."""
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Agregar Excel
        if os.path.exists(EXCEL_FILE):
            zf.write(EXCEL_FILE, os.path.basename(EXCEL_FILE))
        
        # Agregar todas las facturas de PROCESADOS
        if os.path.exists(PROCESADOS_DIR):
            for file in os.listdir(PROCESADOS_DIR):
                exts = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')
                if file.lower().endswith(exts):
                    zf.write(os.path.join(PROCESADOS_DIR, file), file)
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='facturas_y_archivos.zip'
    )

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

@app.route('/config')
def config():
    """Indica a la app si está en entorno local o online."""
    is_local = platform.system() == 'Windows'
    return jsonify({'is_local': is_local})

@app.route('/status')
def status():
    is_local = platform.system() == 'Windows'
    if is_local:
        # En local, el estado depende de lo que haya físicamente en la carpeta
        pending_count = count_files(NO_PROCESADOS_DIR)
        processed_count = session.get('processed', 0)
        return jsonify({
            'no_procesados': pending_count,
            'procesados': processed_count
        })
    else:
        # En online, dependemos de la sesión (lo que se acaba de subir)
        return jsonify({
            'no_procesados': session.get('pending', 0),
            'procesados': session.get('processed', 0)
        })

@app.route('/learn-supplier', methods=['POST'])
def learn_supplier():
    """Guarda una nueva regla de reconocimiento en knowledge.json."""
    data = request.json
    supplier_name = data.get('name')
    new_token = data.get('token')
    # Nuevos campos opcionales para valores por defecto
    default_ncf = data.get('ncf', 'B0100000000')
    default_itbis = float(data.get('itbis', 0))
    default_total = float(data.get('total', 1000))
    
    if not supplier_name or not new_token:
        return jsonify({"success": False, "message": "Datos incompletos"}), 400
        
    knowledge_path = os.path.join(BASE_DIR, 'SKILLS', 'InvoiceProcessor', 'knowledge.json')
    try:
        if not os.path.exists(knowledge_path):
            knowledge = {"suppliers": []}
        else:
            with open(knowledge_path, 'r', encoding='utf-8') as f:
                knowledge = json.load(f)

        # Buscar si el suplidor ya existe para añadirle el token
        found = False
        for s in knowledge['suppliers']:
            if s['name'].lower() == supplier_name.lower():
                if new_token.lower() not in [t.lower() for t in s['tokens']]:
                    s['tokens'].append(new_token.lower())
                # Actualizar datos por defecto si se proporcionan
                if 'default_data' not in s: s['default_data'] = {}
                s['default_data'].update({
                    "NCF": default_ncf,
                    "ITBIS": default_itbis,
                    "Total": default_total
                })
                found = True
                break
        
        if not found:
            knowledge['suppliers'].append({
                "name": supplier_name,
                "tokens": [new_token.lower()],
                "default_data": {
                    "NCF": default_ncf, 
                    "ITBIS": default_itbis, 
                    "Total": default_total
                }
            })
        
        with open(knowledge_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, indent=2, ensure_ascii=False)
            
        return jsonify({"success": True, "message": f"He aprendido que '{new_token}' pertenece a {supplier_name}"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/edit-record', methods=['POST'])
def edit_record():
    """Guarda una corrección para una factura específica en knowledge.json y actualiza el Excel."""
    data = request.json
    supplier_name = data.get('supplier')
    filename = data.get('filename') # El nombre de archivo original o el nuevo
    
    if not supplier_name or not filename:
        return jsonify({"success": False, "message": "Faltan datos del suplidor o archivo"}), 400

    knowledge_path = os.path.join(BASE_DIR, 'SKILLS', 'InvoiceProcessor', 'knowledge.json')
    try:
        with open(knowledge_path, 'r', encoding='utf-8') as f:
            knowledge = json.load(f)
        
        # 1. Buscar el suplidor
        target_supplier = None
        for s in knowledge['suppliers']:
            if s['name'].lower() == supplier_name.lower():
                target_supplier = s
                break
        
        if not target_supplier:
            return jsonify({"success": False, "message": "Suplidor no encontrado en la base de conocimientos"}), 404
        
        # 2. Guardar el override por nombre de archivo
        if 'filename_overrides' not in target_supplier:
            target_supplier['filename_overrides'] = {}
            
        # Limpiar el nombre de archivo (usar solo el basename por si viene con ruta)
        basename = os.path.basename(filename)
        
        target_supplier['filename_overrides'][basename] = {
            "Fecha": data.get('fecha'),
            "Factura": data.get('factura'),
            "NCF": data.get('ncf'),
            "Fecha Vencimiento": data.get('vencimiento'),
            "ITBIS": float(data.get('itbis', 0)),
            "Total": float(data.get('total', 0))
        }
        
        with open(knowledge_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, indent=2, ensure_ascii=False)
            
        # 3. Forzar actualización del reporte Excel
        # Cargamos todos los registros (que ahora incluirán el nuevo override al ser procesados)
        # Pero como queremos que sea inmediato, podemos re-procesar o simplemente avisar.
        # Lo más robusto es re-generar el excel con los nuevos datos.
        
        # Para simplificar, devolvemos éxito y el frontend puede pedir un refresh o re-procesar.
        # Pero mejor intentamos actualizar el Excel directamente si estamos en local.
        is_local = platform.system() == 'Windows'
        if is_local:
            # Re-procesamos para que el Excel se actualice con la nueva "verdad" de knowledge.json
            process_invoices.main()
            
        return jsonify({
            "success": True, 
            "message": f"Registro actualizado para {basename}. El sistema recordará estos valores."
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/process', methods=['POST'])
def process():
    try:
        # 1. Limpiar carpeta PROCESADOS antes de iniciar cada lote
        if os.path.exists(PROCESADOS_DIR):
            for f in os.listdir(PROCESADOS_DIR):
                file_path = os.path.join(PROCESADOS_DIR, f)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error al limpiar {file_path}: {e}")

        # 2. Ejecutar la skill
        newly_processed, failed_files = process_invoices.main()
        
        # 3. Actualizar contadores de sesión
        count = len(newly_processed)
        session['processed'] = count
        session['pending'] = 0
        
        return jsonify({
            'success': True,
            'message': f'Se procesaron {len(newly_processed)} facturas.',
            'data': newly_processed,
            'unknown_files': failed_files # Archivos que requieren "aprendizaje"
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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
