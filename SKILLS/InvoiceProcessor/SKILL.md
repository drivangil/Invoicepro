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
- **Nombre del Suplidor**
- **Fecha de la factura** e **Instancia de Vencimiento**
- **Número de la factura** y **NCF (Comprobante Fiscal)**
- **Total facturado**

- **Nombre de Hoja "Facturas"**: El reporte principal se genera en una pestaña llamada "Facturas".
- **Acumulación de Datos Inteligente**: Permite agregar nuevas facturas al reporte existente, deduplicando por NCF.
- **Orden de Vencimiento Ascendente**: Las facturas se listan por fecha de vencimiento (lo más próximo arriba).
- **Totales Generales**: El reporte incluye una fila final de "TOTAL GENERAL" que suma las columnas ITBIS y Total.
- **Ancho Automático Dinámico**: El ancho de cada columna se ajusta automáticamente al contenido más largo.

## Renombrado y Preservación de Archivos

Al procesar, los archivos se mueven a `/PROCESADOS` usando:
`[2_caracteres_por_palabra_del_suplidor]_[AAAAMMDD]`

- **Cero Pérdidas**: Si ya existe un archivo con el mismo nombre (ej. misma fecha/suplidor), el sistema añade un sufijo (`_1`, `_2`) para preservar todas las imágenes originales.

## Uso

### Opción 1: Aplicación Web (Recomendado)
```powershell
py -3.11 app.py
```
### Opción 2: Script Directo
```powershell
py -3.11 SKILLS/InvoiceProcessor/scripts/process_invoices.py
```

