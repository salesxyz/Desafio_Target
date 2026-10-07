# pyright: reportMissingImports=false
import json
from decimal import Decimal

import pytest

from exercicio1 import comissao


@pytest.mark.parametrize(
    "valor, esperado",
    [
        ("0", "0"),
        ("99.99", "0"),          # abaixo de 100 não gera comissão
        ("100", "1.00"),         # 100 já entra na faixa de 1%
        ("499.99", "4.9999"),    # ainda 1%
        ("500", "25.00"),        # a partir de 500 é 5%
        ("1000", "50.00"),
    ],
)
def test_faixas_de_comissao(valor, esperado):
    assert comissao.calcular_comissao(Decimal(valor)) == Decimal(esperado)


def test_comissao_e_por_venda_e_nao_pelo_total():
    vendas = [
        {"vendedor": "A", "valor": 50},
        {"vendedor": "A", "valor": 100},
        {"vendedor": "A", "valor": 500},
    ]
    totais = comissao.calcular_totais(vendas)
    # 0 + 1,00 + 25,00. Se aplicasse 5% no total (650) daria 32,50
    assert totais["A"] == Decimal("26.00")


def test_separa_os_vendedores():
    vendas = [
        {"vendedor": "A", "valor": 500},
        {"vendedor": "B", "valor": 200},
    ]
    totais = comissao.calcular_totais(vendas)
    assert totais["A"] == Decimal("25.00")
    assert totais["B"] == Decimal("2.00")


def test_resultado_com_o_json_do_desafio():
    with open(comissao.arquivo, encoding="utf-8") as f:
        dados = json.load(f, parse_float=Decimal)

    totais = comissao.calcular_totais(dados["vendas"])
    resultado = {nome: comissao.formatar_reais(valor) for nome, valor in totais.items()}

    assert resultado == {
        "João Silva": "R$ 495,68",
        "Maria Souza": "R$ 465,95",
        "Carlos Oliveira": "R$ 379,37",
        "Ana Lima": "R$ 404,98",
    }


def test_formatar_reais():
    assert comissao.formatar_reais(Decimal("1234.5")) == "R$ 1.234,50"
    assert comissao.formatar_reais(Decimal("0")) == "R$ 0,00"
