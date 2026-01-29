import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

USAR_EMAIL_REAL = True

EMAIL_REMITENTE = "mathiascalvof1@gmail.com"
PASSWORD_REMITENTE = "pbmatkzgkhxwlswd"



codigos_activos = {}


def generar_codigo():
    return ''.join(random.choices(string.digits, k=6))


def enviar_codigo_recuperacion(email_destino, nombre_usuario):
    codigo = generar_codigo()
    
    codigos_activos[email_destino] = {
        'codigo': codigo,
        'expira': datetime.now() + timedelta(minutes=10),
        'usuario': nombre_usuario
    }
    
    if not USAR_EMAIL_REAL:
        print("\n" + "="*50)
        print(f"EMAIL SIMULADO A: {email_destino}")
        print(f"Usuario: {nombre_usuario}")
        print(f"Código de verificación: {codigo}")
        print(f" Válido por: 10 minutos")
        print("="*50 + "\n")
        return True, f"Código enviado a {email_destino}", codigo
    
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_REMITENTE
        mensaje['To'] = email_destino
        mensaje['Subject'] = "SocialTec - Código de Recuperación"
        
        cuerpo = f'''
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f9fafb;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #2563EB; margin-top: 0;"> SocialTec - Recuperación de Contraseña</h2>
                    <p style="font-size: 16px; color: #374151;">Hola <strong>{nombre_usuario}</strong>,</p>
                    <p style="font-size: 16px; color: #374151;">Has solicitado cambiar tu contraseña. Usa el siguiente código de verificación:</p>
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 12px; text-align: center; margin: 25px 0;">
                        <h1 style="color: white; letter-spacing: 8px; margin: 0; font-size: 36px; font-family: 'Courier New', monospace;">{codigo}</h1>
                    </div>
                    <p style="font-size: 16px; color: #374151;">Este código expira en <strong style="color: #DC2626;">10 minutos</strong>.</p>
                    <p style="font-size: 14px; color: #6b7280;">Si no solicitaste este cambio, puedes ignorar este mensaje con seguridad.</p>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="color: #9ca3af; font-size: 12px; text-align: center; margin: 0;">
                        Este es un mensaje automático de SocialTec. Por favor no respondas a este email.
                    </p>
                </div>
            </body>
        </html>
        '''
        
        mensaje.attach(MIMEText(cuerpo, 'html'))
        
        print(f"Conectando con Gmail para enviar a {email_destino}...")
        servidor = smtplib.SMTP(smtp_server, smtp_port)
        servidor.starttls()
        servidor.login(EMAIL_REMITENTE, PASSWORD_REMITENTE)
        servidor.send_message(mensaje)
        servidor.quit()
        
        print(f"Email enviado exitosamente a {email_destino}")
        return True, "Código enviado exitosamente a tu email", codigo
        
    except smtplib.SMTPAuthenticationError:
        error_msg = "Error de autenticación. Verifica tu email y contraseña de aplicación."
        print(f"Error: {error_msg}")
        return False, error_msg, None
    except smtplib.SMTPException as e:
        error_msg = f"Error SMTP: {str(e)}"
        print(f"Error: {error_msg}")
        return False, "Error al enviar email. Intenta nuevamente.", None
    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        print(f"Error: {error_msg}")
        return False, "Error al enviar email. Verifica tu conexión.", None


def verificar_codigo(email, codigo_ingresado):
    if email not in codigos_activos:
        return False, "No hay código activo para este email"
    
    datos = codigos_activos[email]
    
    if datetime.now() > datos['expira']:
        del codigos_activos[email]
        return False, "El código ha expirado"
    
    if datos['codigo'] == codigo_ingresado:
        del codigos_activos[email]
        return True, "Código válido"
    else:
        return False, "Código incorrecto"


def limpiar_codigos_expirados():
    ahora = datetime.now()
    emails_expirados = [
        email for email, datos in codigos_activos.items()
        if ahora > datos['expira']
    ]
    
    for email in emails_expirados:
        del codigos_activos[email]

