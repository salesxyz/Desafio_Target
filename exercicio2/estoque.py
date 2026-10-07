import json
import os
from datetime import datetime

pasta = os.path.dirname(os.path.abspath(__file__))
arquivo = os.path.join(pasta, "estoque.json")

descricoes_entrada = ["Compra de fornecedor", "Devolução de cliente", "Ajuste de inventário"]
descricoes_saida = ["Venda", "Perda/avaria", "Ajuste de inventário"]


def salvar(dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar():
    # se o arquivo não existir ou estiver quebrado, começa vazio
    try:
        with open(arquivo, encoding="utf-8") as f:
            dados = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Não consegui ler o estoque.json, começando vazio.")
        dados = {}

    if "estoque" not in dados:
        dados["estoque"] = []
    if "movimentacoes" not in dados:
        dados["movimentacoes"] = []
    return dados


def buscar_produto(dados, codigo):
    for produto in dados["estoque"]:
        if produto["codigoProduto"] == codigo:
            return produto
    return None


def gerar_id(dados):
    maior = 0
    for mov in dados["movimentacoes"]:
        if mov["id"] > maior:
            maior = mov["id"]
    return maior + 1


def registrar_movimentacao(dados, codigo, tipo, quantidade, descricao):
    # aqui fica toda a regra, sem input nem print, assim dá para testar.
    # se alguma coisa estiver errada levanta ValueError e nada é alterado
    produto = buscar_produto(dados, codigo)
    if produto is None:
        raise ValueError("Produto não encontrado.")
    if tipo != "entrada" and tipo != "saida":
        raise ValueError("Tipo de movimentação inválido.")
    if quantidade <= 0:
        raise ValueError("A quantidade precisa ser maior que zero.")
    # não deixa o estoque ficar negativo
    if tipo == "saida" and quantidade > produto["estoque"]:
        raise ValueError(
            f"Estoque insuficiente. Você tem {produto['estoque']} e pediu {quantidade}."
        )

    saldo_anterior = produto["estoque"]
    if tipo == "entrada":
        produto["estoque"] = produto["estoque"] + quantidade
    else:
        produto["estoque"] = produto["estoque"] - quantidade

    mov = {
        "id": gerar_id(dados),
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "codigoProduto": codigo,
        "tipo": tipo,
        "descricao": descricao,
        "quantidade": quantidade,
        "saldoAnterior": saldo_anterior,
        "saldoFinal": produto["estoque"],
    }
    dados["movimentacoes"].append(mov)
    return mov


def mostrar_estoque(dados):
    print("\nCódigo | Produto | Estoque")
    for p in dados["estoque"]:
        print(p["codigoProduto"], "|", p["descricaoProduto"], "|", p["estoque"])


def mostrar_movimentacoes(dados):
    if len(dados["movimentacoes"]) == 0:
        print("\nNenhuma movimentação ainda.")
        return

    print("\nID | Data | Código | Tipo | Quantidade | Descrição")
    for m in dados["movimentacoes"]:
        print(m["id"], "|", m["data"], "|", m["codigoProduto"], "|", m["tipo"], "|", m["quantidade"], "|", m["descricao"])


def ler_numero(texto):
    try:
        return int(input(texto))
    except ValueError:
        print("Digite só números inteiros.")
        return None


def escolher_descricao(opcoes):
    print("Descrição da movimentação:")
    numero = 1
    for opcao in opcoes:
        print(numero, "-", opcao)
        numero += 1

    escolha = ler_numero("Escolha: ")
    if escolha is None or escolha < 1 or escolha > len(opcoes):
        print("Opção inválida.")
        return None
    return opcoes[escolha - 1]


def lancar(dados, tipo):
    mostrar_estoque(dados)

    codigo = ler_numero("\nCódigo do produto: ")
    if codigo is None:
        return

    produto = buscar_produto(dados, codigo)
    if produto is None:
        print("Produto não encontrado.")
        return

    quantidade = ler_numero("Quantidade: ")
    if quantidade is None:
        return

    if tipo == "entrada":
        descricao = escolher_descricao(descricoes_entrada)
    else:
        descricao = escolher_descricao(descricoes_saida)
    if descricao is None:
        return

    try:
        mov = registrar_movimentacao(dados, codigo, tipo, quantidade, descricao)
    except ValueError as erro:
        print("Erro:", erro)
        return

    salvar(dados)

    print("\nMovimentação", mov["id"], "registrada:", descricao)
    print("Estoque final de", produto["descricaoProduto"] + ":", produto["estoque"])


def main():
    dados = carregar()

    while True:
        print("\n=== CONTROLE DE ESTOQUE ===")
        print("1 - Entrada")
        print("2 - Saída")
        print("3 - Ver estoque")
        print("4 - Ver movimentações")
        print("0 - Sair")
        opcao = input("Opção: ").strip()

        if opcao == "1":
            lancar(dados, "entrada")
        elif opcao == "2":
            lancar(dados, "saida")
        elif opcao == "3":
            mostrar_estoque(dados)
        elif opcao == "4":
            mostrar_movimentacoes(dados)
        elif opcao == "0":
            print("Até logo!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
