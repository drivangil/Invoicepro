---
name: InvoiceProcessorPro
description: Automatización de procesamiento de facturas con extracción de NCF/Vencimiento, reportes agrupados con subtotales, ancho dinámico y renombrado inteligente.
---

# Invoice Processor Pro

Esta skill automatiza el procesamiento de facturas representadas en imágenes, extrayendo datos clave y generando reportes profesionales en Excel.

## Requisitos

- Python 3.10+
- Librerías: `openpyxl`, `pillow`

Instalación de dependencias:
```powershell
pip install openpyxl pillow
```

## Estructura de Carpetas

- `/NO PROCESADOS`: Coloca las imágenes de las facturas aquí.
- `/PROCESADOS`: Las imágenes se mueven aquí con un **nombre inteligente**.
- `facturas.xlsx`: Archivo Excel generado con el **reporte avanzado** en la carpeta raíz del proyecto.

## Capacidades de Extracción

La skill extrae automáticamente:
- **Nombre del Suplidor** (Detección por Pesos y Tokens)
- **Fecha de la factura** (Inferencia por nombre de archivo o OCR simulado)
- **Número de la factura** y **NCF (Comprobante Fiscal)**
- **Total facturado e ITBIS** (Matching de archivo flexible y persistente)
- **Vencimiento Inteligente** (+30 días automático si no se detecta)

### Memoria de Aprendizaje (`knowledge.json`)
La inteligencia de la skill ya no es estática. Utiliza un sistema de **aprendizaje dinámico**:
- **Tokens de Identidad**: Cada suplidor se identifica por un conjunto de palabras clave con pesos.
- **Auto-Aprendizaje**: Si la app no reconoce un suplidor, permite al usuario "enseñarle" desde la interfaz, guardando la regla en `knowledge.json` para futuros reconocimientos automáticos.
- **Matching Flexible**: El sistema asocia datos históricos incluso si el nombre del archivo subido es diferente (ej. `Factura_02.jpg` matchea con `02.jpg`), permitiendo una mayor tasa de acierto en la nube.
- **Fuente de Verdad**: Los suplidores soportados se gestionan directamente en `knowledge.json`.

- **Motor de Tokens (Resiliencia)**: La skill descompone el nombre del archivo y busca coincidencias por pesos. Esto elimina el fallo por "casi-aciertos" y permite detectar suplidores incluso con nombres de archivo desordenados.
- **Arquitectura de Aprendizaje**: Permite la expansión del sistema a nuevos suplidores sin necesidad de modificar el código fuente.
- **Detección Granular por Fecha**: Valida la fecha embebida en el nombre para evitar colisiones entre facturas del mismo proveedor.
- **Acumulación de Datos**: Permite agregar nuevas facturas al reporte existente en modo local, deduplicando por NCF.

## Uso

### Opción 1: Aplicación Web (Local o Nube)
- Local: `python app.py` (acceso en `localhost:5000`)
- Nube: [https://invoicepro.onrender.com](https://invoicepro.onrender.com)

### Opción 2: Script Directo (Skill)
```powershell
python SKILLS/InvoiceProcessor/scripts/process_invoices.py
```

