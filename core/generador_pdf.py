# core/generador_pdf.py
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from core.modelos import Trabajador, ParametrosPeriodo
from core.utils import formato_clp, numero_a_letras, mes_en_espanol, nombre_archivo_seguro

class NumeracionCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#666666"))
        self.drawRightString(letter[0] - 40, 20, f"Página {self._pageNumber} de {total_pages}")
        self.restoreState()

class GeneradorPDF:
    def __init__(self, output_dir: str | Path = "output"):
        self.output_dir = Path(output_dir)

    def generar(self, trabajador: Trabajador, param: ParametrosPeriodo, empresa_info: dict) -> Path:
        ano, mes_num = trabajador.periodo.split("-") if "-" in trabajador.periodo else ("2025", "01")
        mes_nombre = mes_en_espanol(trabajador.hoja)
        
        dir_salida = self.output_dir / ano / mes_num
        dir_salida.mkdir(parents=True, exist_ok=True)
        
        apellido = nombre_archivo_seguro(trabajador.nombre_completo.split()[-1] if trabajador.nombre_completo else "Trabajador")
        ruta_pdf = dir_salida / f"Liquidacion_{trabajador.periodo}_{trabajador.id_trabajador}_{apellido}.pdf"

        doc = SimpleDocTemplate(str(ruta_pdf), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        
        estilo_titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=14, alignment=1, textColor=colors.HexColor("#1A365D"))
        estilo_sub = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=9, alignment=1, textColor=colors.HexColor("#4A5568"))
        estilo_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold')
        estilo_normal = ParagraphStyle('Norm', parent=styles['Normal'], fontSize=9)
        estilo_celda = ParagraphStyle('Celda', parent=styles['Normal'], fontSize=8)

        story = []
        story.append(Paragraph(f"<b>{empresa_info.get('nombre', 'EMPRESA')}</b> — RUT: {empresa_info.get('rut', '')}", estilo_sub))
        story.append(Paragraph("<b>LIQUIDACIÓN DE SUELDO</b>", estilo_titulo))
        story.append(Paragraph(f"Período: {mes_nombre} {ano}", estilo_sub))
        story.append(Spacer(1, 10))

        datos_trab = [
            [Paragraph("<b>Nombre:</b>", estilo_celda), Paragraph(trabajador.nombre_completo, estilo_celda), Paragraph("<b>RUT:</b>", estilo_celda), Paragraph(trabajador.rut, estilo_celda)],
            [Paragraph("<b>ID Trabajador:</b>", estilo_celda), Paragraph(trabajador.id_trabajador, estilo_celda), Paragraph("<b>Cargo:</b>", estilo_celda), Paragraph(trabajador.cargo, estilo_celda)],
            [Paragraph("<b>Contrato:</b>", estilo_celda), Paragraph(trabajador.tipo_contrato, estilo_celda), Paragraph("<b>Días Trab.:</b>", estilo_celda), Paragraph(str(trabajador.dias_trabajados), estilo_celda)],
            [Paragraph("<b>AFP:</b>", estilo_celda), Paragraph(trabajador.afp, estilo_celda), Paragraph("<b>Salud:</b>", estilo_celda), Paragraph(f"{trabajador.institucion_salud}", estilo_celda)]
        ]
        t_datos = Table(datos_trab, colWidths=[80, 190, 70, 190])
        t_datos.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")), ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")), ('PADDING', (0,0), (-1,-1), 4)]))
        story.append(t_datos)
        story.append(Spacer(1, 10))

        haberes_rows = [
            [Paragraph("<b>HABERES</b>", estilo_bold), Paragraph("<b>MONTO ($)</b>", estilo_bold)],
            [Paragraph(f"Sueldo Base", estilo_normal), Paragraph(formato_clp(trabajador.sueldo_devengado), estilo_normal)],
        ]
        if trabajador.monto_horas_extras > 0:
            haberes_rows.append([Paragraph("Horas Extras", estilo_normal), Paragraph(formato_clp(trabajador.monto_horas_extras), estilo_normal)])
        if trabajador.bonos_imponibles > 0:
            haberes_rows.append([Paragraph("Bonos Imponibles", estilo_normal), Paragraph(formato_clp(trabajador.bonos_imponibles), estilo_normal)])
        haberes_rows.append([Paragraph("<b>TOTAL IMPONIBLE</b>", estilo_bold), Paragraph(f"<b>{formato_clp(trabajador.total_imponible)}</b>", estilo_bold)])
        haberes_rows.append([Paragraph("Colación y Movilización", estilo_normal), Paragraph(formato_clp(trabajador.haberes_no_imponibles), estilo_normal)])
        haberes_rows.append([Paragraph("<b>TOTAL HABERES</b>", estilo_bold), Paragraph(f"<b>{formato_clp(trabajador.total_haberes)}</b>", estilo_bold)])

        descuentos_rows = [
            [Paragraph("<b>DESCUENTOS</b>", estilo_bold), Paragraph("<b>MONTO ($)</b>", estilo_bold)],
            [Paragraph(f"AFP ({trabajador.afp})", estilo_normal), Paragraph(formato_clp(trabajador.monto_afp), estilo_normal)],
            [Paragraph(f"Salud", estilo_normal), Paragraph(formato_clp(trabajador.cotizacion_salud), estilo_normal)],
            [Paragraph("Seguro Cesantía", estilo_normal), Paragraph(formato_clp(trabajador.seguro_cesantia_trabajador), estilo_normal)],
            [Paragraph("Impuesto Único", estilo_normal), Paragraph(formato_clp(trabajador.impuesto_unico), estilo_normal)],
            [Paragraph("<b>TOTAL DESCUENTOS</b>", estilo_bold), Paragraph(f"<b>{formato_clp(trabajador.total_descuentos)}</b>", estilo_bold)]
        ]

        t_hab = Table(haberes_rows, colWidths=[180, 85])
        t_hab.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")), ('PADDING', (0,0), (-1,-1), 3)]))

        t_desc = Table(descuentos_rows, colWidths=[180, 85])
        t_desc.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")), ('PADDING', (0,0), (-1,-1), 3)]))

        story.append(Table([[t_hab, t_desc]], colWidths=[265, 265]))
        story.append(Spacer(1, 10))

        monto_letras = numero_a_letras(int(trabajador.liquido_a_pagar))
        liquido_data = [
            [Paragraph("<b>LÍQUIDO A PAGAR:</b>", ParagraphStyle('L1', parent=styles['Normal'], fontSize=11, textColor=colors.white)),
             Paragraph(f"<b>{formato_clp(trabajador.liquido_a_pagar)}</b>", ParagraphStyle('L2', parent=styles['Normal'], fontSize=12, alignment=2, textColor=colors.white))],
            [Paragraph(f"Son: <i>{monto_letras.capitalize()}</i>", ParagraphStyle('L3', parent=styles['Normal'], fontSize=9, textColor=colors.white)), ""]
        ]
        t_liq = Table(liquido_data, colWidths=[200, 330])
        t_liq.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1A365D")), ('SPAN', (0, 1), (1, 1)), ('PADDING', (0,0), (-1,-1), 6)]))
        story.append(t_liq)
        story.append(Spacer(1, 10))

        story.append(Paragraph(f"• Aporte Empleador Seguro Cesantía: {formato_clp(trabajador.seguro_cesantia_empleador)} | UF: ${param.valor_uf:,.2f} | UTM: ${param.valor_utm:,.2f}", estilo_celda))
        story.append(Paragraph("Declaro haber recibido conforme el monto indicado y no tener cobro posterior que hacer.", estilo_celda))
        story.append(Spacer(1, 25))

        t_firmas = Table([[Paragraph("___________________________________<br/>Firma Empleador", ParagraphStyle('F1', parent=styles['Normal'], alignment=1, fontSize=8)),
                           Paragraph("___________________________________<br/>Firma Trabajador", ParagraphStyle('F2', parent=styles['Normal'], alignment=1, fontSize=8))]], colWidths=[250, 250])
        story.append(t_firmas)

        doc.build(story, canvasmaker=NumeracionCanvas)
        return ruta_pdf