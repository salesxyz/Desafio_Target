import json
import os
from decimal import Decimal, ROUND_HALF_UP

pasta = os.path.dirname(os.path.abspath(__file__))
arquivo = os.path.join(pasta, "vendas.json")


def calcular_comissao(valor):
    # a regra vale para cada venda, não para o total do vendedor
    if valor < 100:
        return Decimal("0")
    elif valor < 500:
        return valor * Decimal("0.01")
    else:
        return valor * Decimal("0.05")


def calcular_totais(vendas):
    totais = {}
    for venda in vendas:
        nome = venda["vendedor"]
        # str() antes do Decimal para não pegar a imprecisão do float
        valor = Decimal(str(venda["valor"]))

        if nome not in totais:
            totais[nome] = Decimal("0")
        totais[nome] = totais[nome] + calcular_comissao(valor)
    return totais


def formatar_reais(valor):
    valor = valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    texto = f"{valor:,.2f}"
    # troca o formato americano (1,234.56) pelo brasileiro (1.234,56)
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + texto


def main():
    # parse_float=Decimal para não ter erro de arredondamento com float
    with open(arquivo, encoding="utf-8") as f:
        dados = json.load(f, parse_float=Decimal)

    totais = calcular_totais(dados["vendas"])

    print("Comissão por vendedor")
    print("-" * 36)
    for nome in sorted(totais):
        print(f"{nome:<18} {formatar_reais(totais[nome]):>16}")


if __name__ == "__main__":
    main()
