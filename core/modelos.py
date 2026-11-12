# core/modelos.py
from dataclasses import dataclass

@dataclass
class Trabajador:
    rut: str = ""
    nombre: str = ""
    sueldo_base: float = 0.0
    dias_trabajados: int = 30

@dataclass
class ParametrosPeriodo:
    mes: str = ""
    anio: int = 2026
    uf: float = 0.0
    utm: float = 0.0
    sueldo_minimo: float = 0.0