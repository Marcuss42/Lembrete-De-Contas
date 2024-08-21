import locale
from datetime import datetime
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from json import load, dump
import send_email

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
send_email.destinatario = "gislaniafrnacisco@gmail.com"

app = Flask(__name__)

contas = load(open("contas.json"))

def enviar_email():
    for nome_conta, info in contas.items():
        meses_nao_pagos, vencimento = info.values()
        if datetime.now().day == int(vencimento) - 2:
            send_email.assunto = f"AVISO: A conta {nome_conta} irá vencer no dia {vencimento}"
            for mes in meses_nao_pagos:
                send_email.conteudo += f'\n\n<a href="http://127.0.0.1:5000//confirmar_pagamento/{nome_conta}/{mes}">Confirmar pagamento - {mes}</a>'
            send_email.send()
            print("Email enviado")
            send_email.conteudo = ''

def save(): dump(contas, open("contas.json", "w"), indent=4)

def adicionar_mes_auto():
    hoje = datetime.now()
    mes_atual = hoje.strftime('%B')  
    dia_atual = hoje.day

    for conta, info in contas.items():
        if info['vencimento'] == str(dia_atual):
            if mes_atual not in info['meses_nao_pagos']:
                info['meses_nao_pagos'].append(mes_atual)
                print(f"Novo mês {mes_atual} adicionado à conta {conta}.")
    save()
 
@app.route('/', methods=['GET'])
def home():
    return jsonify(contas)

@app.route('/verificar_adicao', methods=['GET'])
def verificar_adicao():
    adicionar_mes_auto()
    save()
    return jsonify(contas)


@app.route('/confirmar_pagamento/<conta>/<mes>', methods=['GET'])
def confirmar_pagamento(conta, mes):
    if conta in contas:
        conta_info = contas[conta]
        if mes in conta_info["meses_nao_pagos"]:
            conta_info["meses_nao_pagos"].remove(mes)
            save()
            if not conta_info["meses_nao_pagos"]:
                return jsonify(message=f"Todos os pagamentos para a conta {conta.capitalize()} foram confirmados!"), 200
            else:
                return jsonify(message=f"O pagamento da conta {conta.capitalize()} para o mes {mes} foi confirmado!"), 200
        else:
            return jsonify(message=f"O mes {mes} nao esta em atraso ou ja foi pago."), 404
    else:
        return jsonify(message="Conta nao encontrada."), 404


@app.route('/adicionar_mes/<conta>/<mes>', methods=['GET'])
def adicionar_mes(conta, mes):
    if conta in contas:
        conta_info = contas[conta]
        if mes not in conta_info["meses_nao_pagos"]:
            conta_info["meses_nao_pagos"].append(mes)
            save()
            return jsonify(message=f"O mes {mes} foi adicionado à conta {conta.capitalize()} como nao pago."), 200
        else:
            return jsonify(message=f"O mes {mes} ja esta marcado como nao pago para a conta {conta.capitalize()}.") , 400
    else:
        return jsonify(message="Conta não encontrada."), 404
    

@app.route('/adicionar_conta/<conta>/<vencimento>', methods=['GET'])
def adicionar_conta(conta, vencimento):
    contas[conta] = {
            "meses_nao_pagos": [datetime.now().strftime("%B")],
            "vencimento": vencimento
    }

    save()

    return jsonify(contas)

scheduler = BackgroundScheduler()
scheduler.add_job(adicionar_mes_auto, 'interval', days=30)
scheduler.add_job(enviar_email, 'interval', days=1)
adicionar_mes_auto()

if __name__ == '__main__':
    scheduler.start()
    app.run(debug=True)
