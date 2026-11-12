import re
from num2words import num2words

def validar_rut(rut: str) -> bool:
    if not rut or not isinstance(rut, str):
        return False
    rut_limpio = rut.replace(".", "").replace(" ", "").upper()
    match = re.match(r"^(\d+)-([0-9K])$", rut_limpio)
    if not match:
        return False
    cuerpo, dv = match.groups()
    suma = 0
    multiplicador = 2
    for r in reversed(cuerpo):
        suma += int(r) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    resto = suma % 11
    resultado = 11 - resto
    if resultado == 11:
        dv_esperado = "0"
    elif resultado == 10:
        dv_esperado = "K"
    else:
        dv_esperado = str(resultado)
    return dv == dv_esperado

def enmascarar_rut(rut: str) -> str:
    if not rut:
        return ""
    rut_limpio = rut.replace(".", "").replace(" ", "").upper()
    match = re.match(r"^(\d+)-([0-9K])$", rut_limpio)
    if not match:
        return "***"
    cuerpo, dv = match.groups()
    if len(cuerpo) <= 3:
        return f"***-{dv}"
    cuerpo_enmascarado = cuerpo[:-3] + "***"
    # Formatear con puntos opcionalmente o simple
    return f"{cuerpo_enmascarado}-{dv}"

def formato_clp(valor: int) -> str:
    try:
        val_int = int(round(float(valor)))
    except (ValueError, TypeError):
        val_int = 0
    # Separador de miles con punto
    s = f"{abs(val_int):,}".replace(",", ".")
    if val_int < 0:
        return f"-${s}"
    return f"${s}"

def numero_a_letras(numero: int) -> str:
    if numero == 0:
        return "cero pesos"
    try:
        texto = num2words(numero, lang='es')
        # Ajustes chilenos comunes si fuera necesario (ej. veintiún mil)
        texto = texto.replace("mil uno", "mil uno")
        return f"{texto} pesos"
    except Exception:
        return f"{numero} pesos"

def mes_en_espanol(mes_num: int) -> str:
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    return meses.get(mes_num, "Mes")

def nombre_archivo_seguro(texto: str) -> str:
    if not texto:
        return "desconocido"
    reemplazos = (
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
        ("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U"),
        ("ñ", "n"), ("Ñ", "N")
    )
    for a, b in reemplazos:
        texto = texto.replace(a, b)
    texto = re.sub(r'[\\/*?:"<>|]', "", texto)
    texto = re.sub(r'\s+', "_", texto.strip())
    return texto