# core/registro.py
import logging
import csv
from pathlib import Path
from datetime import datetime
from typing import List
from core.modelos import ResultadoEnvio

class GestorRegistro:
    def __init__(self, log_dir: str | Path = "logs", output_dir: str | Path = "output"):
        self.log_dir = Path(log_dir)
        self.output_dir = Path(output_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.log_file = self.log_dir / f"liquidaciones_{timestamp}.log"
        self.resultados_file = self.output_dir / f"resultados_{timestamp}.csv"
        
        logging.basicConfig(filename=self.log_file, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", encoding="utf-8")
        self.logger = logging.getLogger("Liquidaciones")

    def info(self, mensaje: str):
        self.logger.info(mensaje)
        print(f"[INFO] {mensaje}")

    def warning(self, mensaje: str):
        self.logger.warning(mensaje)
        print(f"[ADVERTENCIA] {mensaje}")

    def error(self, mensaje: str):
        self.logger.error(mensaje)
        print(f"[ERROR] {mensaje}")

    def guardar_resultados_csv(self, resultados: List[ResultadoEnvio]):
        with open(self.resultados_file, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Período", "ID Trabajador", "Nombre", "Correo", "PDF Generado", "Ruta PDF", "Correo Enviado", "Fecha Envío", "Intentos", "Error"])
            for r in resultados:
                writer.writerow([r.periodo, r.id_trabajador, r.nombre, r.correo, "Sí" if r.pdf_generado else "No", r.pdf_ruta or "", "Sí" if r.correo_enviado else "No", r.fecha_envio or "", r.intentos, r.mensaje_error or ""])
        self.info(f"Planilla de resultados guardada en: {self.resultados_file}")