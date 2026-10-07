from datetime import date, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from exercicio3 import juros

client = TestClient(juros.app)


# ---- função de cálculo (com data fixa, para o teste não depender do dia de hoje)

def test_juros_de_10_dias_de_atraso():
    dias, valor_juros = juros.calcular(Decimal("1000"), date(2026, 9, 27), date(2026, 10, 7))

    assert dias == 10
    assert valor_juros == Decimal("250.000")  # 1000 x 2,5% x 10


def test_vence_hoje_nao_tem_juros():
    dias, valor_juros = juros.calcular(Decimal("1000"), date(2026, 10, 7), date(2026, 10, 7))

    assert dias == 0
    assert valor_juros == 0


def test_ainda_nao_venceu_nao_tem_juros():
    dias, valor_juros = juros.calcular(Decimal("1000"), date(2026, 10, 12), date(2026, 10, 7))

    assert dias == 0
    assert valor_juros == 0


def test_arredondamento_para_centavos():
    # 1000,50 x 2,5% x 3 = 75,0375 -> 75,04
    _, valor_juros = juros.calcular(Decimal("1000.50"), date(2026, 10, 4), date(2026, 10, 7))

    assert juros.arredondar(valor_juros) == Decimal("75.04")


# ---- endpoint

def test_endpoint_calcula_juros():
    vencimento = date.today() - timedelta(days=10)

    resposta = client.post("/juros", json={"valor": 1000, "vencimento": str(vencimento)})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["dias_atraso"] == 10
    assert corpo["juros"] == 250.0
    assert corpo["valor_total"] == 1250.0
    assert corpo["data_calculo"] == str(date.today())


def test_endpoint_sem_atraso():
    vencimento = date.today() + timedelta(days=5)

    resposta = client.post("/juros", json={"valor": 500, "vencimento": str(vencimento)})

    assert resposta.status_code == 200
    assert resposta.json()["juros"] == 0.0
    assert resposta.json()["valor_total"] == 500.0


def test_endpoint_rejeita_valor_zero_ou_negativo():
    for valor in (0, -10):
        resposta = client.post("/juros", json={"valor": valor, "vencimento": "2026-09-27"})
        assert resposta.status_code == 422


def test_endpoint_rejeita_data_invalida():
    resposta = client.post("/juros", json={"valor": 100, "vencimento": "31/12/2025"})
    assert resposta.status_code == 422
