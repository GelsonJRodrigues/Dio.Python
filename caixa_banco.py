def exibir_menu():
    print("""
    === MENU ===
    [1] Depósito
    [2] Saque
    [3] Extrato
    [0] Sair
    """)

def main():
    saldo = 0.0
    limite_saque = 500.0
    saques_realizados = 0
    limite_saques = 3
    extrato = []

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":  # Depósito
            valor = float(input("Valor para depósito: R$ "))
            if valor > 0:
                saldo += valor
                extrato.append(f"Depósito:    + R$ {valor:.2f}")
                print(f"Depósito de R$ {valor:.2f} realizado com sucesso.")
            else:
                print("Operação falhou: valor inválido para depósito.")

        elif opcao == "2":  # Saque
            if saques_realizados >= limite_saques:
                print("Limite de saques diários atingido (3 por dia).")
                continue

            valor = float(input("Valor para saque:    R$ "))
            if valor <= 0:
                print("Operação falhou: valor inválido para saque.")
            elif valor > saldo:
                print("Operação falhou: saldo insuficiente.")
            elif valor > limite_saque:
                print(f"Operação falhou: valor excede o limite de R$ {limite_saque:.2f}.")
            else:
                saldo -= valor
                saques_realizados += 1
                extrato.append(f"Saque:       - R$ {valor:.2f}")
                print(f"Saque de R$ {valor:.2f} realizado com sucesso.")

        elif opcao == "3":  # Extrato
            print("\n===== EXTRATO =====")
            if not extrato:
                print("Não foram realizadas movimentações.")
            else:
                for registro in extrato:
                    print(registro)
            print(f"\nSaldo atual: R$ {saldo:.2f}")
            print("===================\n")

        elif opcao == "0":  # Sair
            print("Encerrando sessão. Obrigado por usar nosso sistema.")
            break

        else:
            print("Opção inválida. Escolha novamente.")

if __name__ == "__main__":
    main()
