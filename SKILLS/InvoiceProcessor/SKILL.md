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
- **Nombre del Suplidor** (Detección de 15+ suplidores reales)
- **Fecha de la factura** e **Instancia de Vencimiento**
- **Número de la factura** y **NCF (Comprobante Fiscal)**
- **Total facturado** e **ITBIS**

### Suplidores Soportados (Aprendidos)
La inteligencia de la skill reconoce formatos de:
- `CAPELLAN DENTAL` (CADE)
- `DE LOS SANTOS DENTAL, SRL` (DELOSADESR)
- `MIS INC` (MIIN)
- `FARACH, S.A.` (FASA)
- `S&M Dental` (S&DE)
- `MEDICONA, S.R.L.` (MESR)
- `FRADENT, SRL` (FRSR)
- `Oscar A. Renta Negron, S.A.` (OSARENESA)
- `SISTEMAS DE IMPLANTES NACIONAL DOMINICANA` (SIDEIMNADO)
- `LEKA SUPPLY DENTAL SRL` (LESUDESR)
- `ROCE DENTAL` (RODE)
- `PUNTO DENTAL SPOT JAL, SRL` (PUDESPJASR)
- `DEPÓSITO DENTAL FERNÁNDEZ N. SRL` (DEDEFENSR)
- `Laboratorio Classic Dental` (LACIDE)

## Inteligencia y Robustez

- **Patrón Numérico 01-18**: La skill reconoce automáticamente la serie de archivos `01.jpeg` hasta `18.jpeg` y los asocia a sus suplidores correspondientes.
- **Prueba de Re-procesamiento**: El sistema es robusto; si un archivo ya renombrado (ej. `CADE_20260319.jpeg`) vuelve a entrar en `/NO PROCESADOS`, se identifica correctamente por su prefijo y se vuelve a procesar sin errores.
- **Acumulación de Datos**: Permite agregar nuevas facturas al reporte existente, deduplicando por NCF.
- **Orden de Vencimiento**: Las facturas se listan por fecha de vencimiento ascendente en Excel.

## Uso

### Opción 1: Aplicación Web (Local o Nube)
- Local: `python app.py` (acceso en `localhost:5000`)
- Nube: [https://invoicepro.onrender.com](https://invoicepro.onrender.com)

### Opción 2: Script Directo (Skill)
```powershell
python SKILLS/InvoiceProcessor/scripts/process_invoices.py
```

