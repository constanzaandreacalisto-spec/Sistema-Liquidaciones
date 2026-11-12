# core/enviador_correo.py
import smtplib
import time
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
from typing import Optional
from jinja2 import Template

class EnviadorCorreo:
    def __init__(self, config: dict):
        self.host = config.get("SMTP_HOST")
        self.port = int(config.get("SMTP_PORT", 587))
        self.user = config.get("SMTP_USER")
        self.password = config.get("SMTP_PASSWORD")
        self.use_tls = config.get("SMTP_USE_TLS", "true").lower() == "true"
        self.from_name = config.get("MAIL_FROM_NAME", "Recursos Humanos")
        self.from_address = config.get("MAIL_FROM_ADDRESS", self.user)
        self.reply_to = config.get("MAIL_REPLY_TO", self.from_address)
        self.delay = float(config.get("MAIL_DELAY_SECONDS", 2))
        self.max_retries = int(config.get("MAIL_MAX_RETRIES", 3))

    def enviar_liquidacion(self, destinatario: str, nombre_trabajador: str, periodo: str, ruta_pdf: str | Path, test_email: Optional[str] = None, dry_run: bool = False) -> bool:
        if dry_run:
            print(f"[DRY-RUN] Simulando envío a {destinatario} (PDF: {ruta_pdf})")
            return True

        correo_destino = test_email if test_email else destinatario
        primer_nombre = nombre_trabajador.split()[0] if nombre_trabajador else "Trabajador"

        msg = EmailMessage()
        msg["Subject"] = f"Liquidación de sueldo – {periodo}"
        msg["From"] = formataddr((self.from_name, self.from_address))
        msg["To"] = correo_destino
        if self.reply_to:
            msg["Add-Reply-To"] = self.reply_to

        try:
            with open("templates/correo.txt", "r", encoding="utf-8") as f:
                txt_template = f.read()
            with open("templates/correo.html", "r", encoding="utf-8") as f:
                html_template = f.read()
        except FileNotFoundError:
            txt_template = "Estimado/a {{nombre}}, adjunto su liquidación."
            html_template = "<p>Estimado/a {{nombre}}, adjunto su liquidación.</p>"

        ctx = {"nombre": primer_nombre, "periodo": periodo, "empresa": self.from_name}
        msg.set_content(Template(txt_template).render(ctx))
        msg.add_alternative(Template(html_template).render(ctx), subtype="html")

        pdf_path = Path(ruta_pdf)
        if pdf_path.exists():
            with open(pdf_path, "rb") as pf:
                msg.add_attachment(pf.read(), maintype="application", subtype="pdf", filename=pdf_path.name)

        intento = 0
        while intento < self.max_retries:
            intento += 1
            try:
                server = smtplib.SMTP(self.host, self.port, timeout=30)
                if self.use_tls:
                    server.starttls()
                if self.user and self.password:
                    server.login(self.user, self.password)
                server.send_message(msg)
                server.quit()
                time.sleep(self.delay)
                return True
            except (smtplib.SMTPAuthenticationError, smplib.SMTPRecipientsRefused) as e:
                print(f"Error permanente enviando a {correo_destino}: {e}")
                return False
            except Exception as e:
                print(f"Error transitorio enviando a {correo_destino} (Intento {intento}/{self.max_retries}): {e}")
                time.sleep(2 ** intento)

        return False