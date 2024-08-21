import yagmail

# Configurações do e-mail
usuario = 'mpfrancisco2003@gmail.com'
senha = 'ixll xgsz kjww fkjv'
destinatario = ''
assunto = 'Teste'
conteudo = 'Teste'

def send():
    yag = yagmail.SMTP(usuario, senha)
    yag.send(
        to=destinatario,
        subject=assunto,
        contents=conteudo,
    )

if __name__ == "__main__":
    send()