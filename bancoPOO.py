from dataclasses import dataclass, field
from datetime import datetime, date
from zoneinfo import ZoneInfo
from typing import List, Dict
import itertools

BR_TZ = ZoneInfo("America/Sao_Paulo")

class SaqueExcedidoError(Exception):
    pass

class SaldoInsuficienteError(Exception):
    pass

@dataclass
class Cliente:
    nome: str
    endereco: str
    cpf: str
    data_nascimento: str  # string no formato YYYY-MM-DD ou similar

@dataclass
class Conta:
    numero: str
    agencia: str
    cliente: Cliente
    saldo: float = 0.0
    historico: List[Dict] = field(default_factory=list)
    limite_saque_diario: float = 500.0

    def _agora(self) -> datetime:
        return datetime.now(tz=BR_TZ)

    def _registrar_historico(self, tipo: str, valor: float, saldo_apos: float):
        entrada = {
            "data_hora": self._agora().isoformat(),
            "tipo": tipo,  # 'depósito' ou 'saque' ou 'criação'
            "valor": round(valor, 2),
            "saldo_apos": round(saldo_apos, 2)
        }
        self.historico.append(entrada)

    def depositar(self, valor: float):
        if valor <= 0:
            raise ValueError("Valor de depósito deve ser maior que zero.")
        self.saldo = round(self.saldo + valor, 2)
        self._registrar_historico("depósito", valor, self.saldo)
        return self.saldo

    def _total_sacado_na_data(self, dia: date) -> float:
        total = 0.0
        for e in self.historico:
            if e["tipo"] == "saque":
                ts = datetime.fromisoformat(e["data_hora"])
                if ts.astimezone(BR_TZ).date() == dia:
                    total += float(e["valor"])
        return round(total, 2)

    def sacar(self, valor: float):
        if valor <= 0:
            raise ValueError("Valor de saque deve ser maior que zero.")
        if valor > self.saldo:
            raise SaldoInsuficienteError("Saldo insuficiente para realizar o saque.")
        hoje = self._agora().date()
        ja_sacado = self._total_sacado_na_data(hoje)
        if (ja_sacado + valor) > self.limite_saque_diario:
            restante = round(self.limite_saque_diario - ja_sacado, 2)
            raise SaqueExcedidoError(
                f"Saque excederia o limite diário de R${self.limite_saque_diario:.2f}. "
                f"Você já sacou R${ja_sacado:.2f} hoje. Restam R${restante:.2f}."
            )
        self.saldo = round(self.saldo - valor, 2)
        self._registrar_historico("saque", valor, self.saldo)
        return self.saldo

    def obter_saldo(self) -> float:
        return round(self.saldo, 2)

    def extrato(self) -> List[Dict]:
        return [dict(e) for e in self.historico]

    def imprimir_extrato(self, mostrar_saldo_final: bool = True):
        print(f"\nExtrato da Conta {self.numero} - Agência {self.agencia}")
        print("-" * 70)
        if not self.historico:
            print("Sem movimentações.")
        else:
            for e in self.historico:
                ts = datetime.fromisoformat(e["data_hora"]).astimezone(BR_TZ)
                ts_str = ts.strftime("%Y-%m-%d %H:%M:%S %Z")
                tipo = e["tipo"].capitalize()
                valor = f"R${e['valor']:.2f}"
                saldo_apos = f"R${e['saldo_apos']:.2f}"
                print(f"{ts_str} | {tipo:10} | {valor:12} | Saldo após: {saldo_apos}")
        if mostrar_saldo_final:
            print("-" * 70)
            print(f"Saldo atual: R${self.obter_saldo():.2f}\n")

# Gerenciamento simples de contas em memória
class BancoSimples:
    def __init__(self, agencia_padrao: str = "0001"):
        self.agencia_padrao = agencia_padrao
        self._contas: Dict[str, Conta] = {}
        # contador para gerar números de conta sequenciais
        self._contador = itertools.count(1)

    def criar_conta_para_cliente(self, cliente: Cliente) -> Conta:
        numero_conta = f"{next(self._contador):04d}-X"  # por exemplo "0001-X"
        conta = Conta(numero=numero_conta, agencia=self.agencia_padrao, cliente=cliente)
        conta._registrar_historico("criação", 0.0, conta.saldo)
        self._contas[numero_conta] = conta
        return conta

    def obter_conta(self, numero: str) -> Conta:
        return self._contas.get(numero)

    def listar_contas(self) -> List[Conta]:
        return list(self._contas.values())

# Funções utilitárias do menu
def ler_float(prompt: str) -> float:
    while True:
        s = input(prompt).strip().replace(",", ".")
        try:
            v = float(s)
            return v
        except ValueError:
            print("Valor inválido. Digite um número, ex: 100.50")

def cadastrar_cliente_e_criar_conta(banco: BancoSimples):
    print("\n=== Cadastro de Cliente e Criação de Conta ===")
    nome = input("Nome completo: ").strip()
    endereco = input("Endereço: ").strip()
    cpf = input("CPF: ").strip()
    data_nasc = input("Data de nascimento (YYYY-MM-DD): ").strip()
    cliente = Cliente(nome=nome, endereco=endereco, cpf=cpf, data_nascimento=data_nasc)
    conta = banco.criar_conta_para_cliente(cliente)
    print(f"\nConta criada com sucesso! Número: {conta.numero} | Agência: {conta.agencia}")
    # Mostrar extrato (será apenas a criação)
    conta.imprimir_extrato()

def realizar_deposito(banco: BancoSimples):
    print("\n=== Depósito ===")
    numero = input("Número da conta: ").strip()
    conta = banco.obter_conta(numero)
    if not conta:
        print("Conta não encontrada.")
        return
    valor = ler_float("Valor a depositar (ex: 150.00): R$ ")
    try:
        conta.depositar(valor)
        print(f"Depósito de R${valor:.2f} realizado com sucesso.")
    except Exception as e:
        print("Erro no depósito:", e)
    # Mostrar histórico sempre após a ação
    conta.imprimir_extrato()

def realizar_saque(banco: BancoSimples):
    print("\n=== Saque ===")
    numero = input("Número da conta: ").strip()
    conta = banco.obter_conta(numero)
    if not conta:
        print("Conta não encontrada.")
        return
    valor = ler_float("Valor a sacar (ex: 100.00): R$ ")
    try:
        conta.sacar(valor)
        print(f"Saque de R${valor:.2f} realizado com sucesso.")
    except SaqueExcedidoError as e:
        print("Saque rejeitado:", e)
    except SaldoInsuficienteError as e:
        print("Saque rejeitado:", e)
    except Exception as e:
        print("Erro no saque:", e)
    # Mostrar histórico sempre após a ação
    conta.imprimir_extrato()

def consultar_saldo(banco: BancoSimples):
    print("\n=== Saldo ===")
    numero = input("Número da conta: ").strip()
    conta = banco.obter_conta(numero)
    if not conta:
        print("Conta não encontrada.")
        return
    print(f"Saldo atual da conta {conta.numero}: R${conta.obter_saldo():.2f}")
    # Mostrar histórico sempre após a ação
    conta.imprimir_extrato()

def listar_contas(banco: BancoSimples):
    print("\n=== Contas cadastradas ===")
    contas = banco.listar_contas()
    if not contas:
        print("Nenhuma conta cadastrada.")
        return
    for c in contas:
        print(f"Conta: {c.numero} | Agência: {c.agencia} | Cliente: {c.cliente.nome} | Saldo: R${c.saldo:.2f}")

def menu_principal():
    banco = BancoSimples()
    opcoes = {
        "1": ("Adicionar cliente e criar conta", cadastrar_cliente_e_criar_conta),
        "2": ("Depósito", realizar_deposito),
        "3": ("Saque", realizar_saque),
        "4": ("Saldo", consultar_saldo),
        "5": ("Listar contas", listar_contas),
        "0": ("Sair", None)
    }

    while True:
        print("\n=== MENU PRINCIPAL ===")
        for k, (desc, _) in opcoes.items():
            print(f"{k} - {desc}")
        escolha = input("Escolha uma opção: ").strip()
        if escolha == "0":
            print("Encerrando. Até mais!")
            break
        acao = opcoes.get(escolha)
        if not acao:
            print("Opção inválida. Tente novamente.")
            continue
        func = acao[1]
        # executar a função, passando o banco
        try:
            func(banco)
        except Exception as e:
            # Protege o loop contra erros inesperados
            print("Ocorreu um erro durante a operação:", e)

if __name__ == "__main__":
    menu_principal()
