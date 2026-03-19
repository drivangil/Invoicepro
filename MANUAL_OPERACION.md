# Manual de Operación - Invoicepro

Este documento contiene las instrucciones necesarias para operar, actualizar y desplegar la aplicación Invoicepro (Procesador de Facturas).

## Ubicación del Proyecto

- **Ruta Local**: `C:\Users\driva\OneDrive\PROCESADOR DE FACTURAS`
- **Repositorio GitHub**: [https://github.com/drivangil/Invoicepro](https://github.com/drivangil/Invoicepro)

## Acceso Online (Producción)

⚠️ **URL IMPORTANTÍSIMA DE RENDER**: [https://invoicepro.onrender.com](https://invoicepro.onrender.com)

- **Descripción**: Esta es la versión que puedes usar desde cualquier lugar y dispositivo.
- **Dashboard de Render**: [https://dashboard.render.com/](https://dashboard.render.com/) (Para ver el estado del servidor si algo falla).

## Procedimiento de Actualización

Cada vez que realices cambios en el código localmente, sigue estos pasos para que se reflejen en la versión online:

1. **Guardar Cambios Localmente (Git)**:
   - Abre una terminal en la carpeta del proyecto.
   - Ejecuta: `git add .`
   - Ejecuta: `git commit -m "Descripción de los cambios"`
2. **Subir a GitHub**:
   - Ejecuta: `git push origin main`
3. **Despliegue Automático**:
   - Render detectará el nuevo "push" en GitHub y comenzará a reconstruir la aplicación automáticamente.
   - Puedes monitorear el progreso en el dashboard de [Render](https://dashboard.render.com/).

## Ejecución Local (Para Pruebas)

Si deseas probar cambios antes de subirlos:
1. Asegúrate de tener Python instalado.
2. Abre la terminal en la carpeta del proyecto.
3. Activa el entorno virtual (si existe) o instala dependencias: `pip install -r requirements.txt`.
4. Ejecuta: `python app.py`.
5. Abre `http://127.0.0.1:5000` en tu navegador.

## Estructura de Carpetas Clave

- `NO PROCESADOS/`: Imágenes de facturas (.png, .jpg) que están pendientes de procesar.
- `PROCESADOS/`: Facturas que ya han sido analizadas.
- `facturas.xlsx`: Archivo Excel con los resultados consolidados.
- `SKILLS/`: Contiene la lógica de procesamiento (Inteligencia Artificial).

---
*Este manual es para uso interno para facilitar el retorno al proyecto después de periodos prolongados.*
