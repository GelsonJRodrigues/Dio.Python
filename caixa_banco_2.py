import datetime

# Dados da conta
saldo = 0.0
transacoes = []
limite_transacoes = 10
limite_saque = 500.0

def registrar_transacao(tipo, valor):
    agora = datetime.datetime.now()
    transacoes.append({
        "tipo": tipo,
        "valor": valor,
        "data_hora": agora.strftime("%d/%m/%Y %H:%M:%S")
    })

def mostrar_menu():
    print("\n=== Caixa Eletrônico ===")
    print("1: Depósito")
    print("2: Saque")
    print("3: Extrato")
    print("0: Sair")

def deposito():
    global saldo
    valor = float(input("Digite o valor para depósito: R$ "))
    if valor > 0:
        saldo += valor
        registrar_transacao("Depósito", valor)
        print(f"Depósito de R$ {valor:.2f} realizado com sucesso.")
    else:
        print("Valor inválido para depósito.")

def saque():
    global saldo
    valor = float(input("Digite o valor para saque: R$ "))
    if valor > limite_saque:
        print(f"Saque não permitido. Limite por operação: R$ {limite_saque:.2f}")
    elif valor > saldo:
        print("Saldo insuficiente.")
    elif valor <= 0:
        print("Valor inválido para saque.")
    else:
        saldo -= valor
        registrar_transacao("Saque", valor)
        print(f"Saque de R$ {valor:.2f} realizado com sucesso.")

def extrato():
    print("\n=== Extrato ===")
    if not transacoes:
        print("Nenhuma transação realizada.")
    else:
        for t in transacoes:
            print(f"{t['data_hora']} - {t['tipo']}: R$ {t['valor']:.2f}")
    print(f"Saldo atual: R$ {saldo:.2f}")

# Loop principal
while True:
    if len(transacoes) >= limite_transacoes:
        print("\n⚠️ Limite de transações diárias atingido. Tente novamente amanhã.")
        break

    mostrar_menu()
    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        deposito()
    elif opcao == "2":
        saque()
    elif opcao == "3":
        extrato()
    elif opcao == "0":
        print("Encerrando o programa. Até logo!")
        break
    else:
        print("Opção inválida. Tente novamente.")
