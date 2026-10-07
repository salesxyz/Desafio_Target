from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Cálculo de juros por atraso")

# 2,5% ao dia
TAXA_DIARIA = Decimal("0.025")


class Titulo(BaseModel):
    valor: Decimal = Field(gt=0, description="Valor original, maior que zero", examples=[1000])
    vencimento: date = Field(description="Data de vencimento no formato AAAA-MM-DD", examples=["2026-09-27"])


class Resultado(BaseModel):
    valor_original: float
    vencimento: date
    data_calculo: date
    dias_atraso: int
    juros: float
    valor_total: float


def arredondar(valor):
    # arredonda para 2 casas (centavos)
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular(valor, vencimento, hoje):
    # quantos dias passaram do vencimento até hoje
    dias_atraso = (hoje - vencimento).days

    # se ainda não venceu, não tem juros
    if dias_atraso < 0:
        dias_atraso = 0

    # juros simples: valor x 2,5% x dias de atraso
    juros = valor * TAXA_DIARIA * dias_atraso
    return dias_atraso, juros


@app.post("/juros", response_model=Resultado)
def calcular_juros(titulo: Titulo):
    hoje = date.today()
    dias_atraso, juros = calcular(titulo.valor, titulo.vencimento, hoje)
    total = titulo.valor + juros

    return {
        "valor_original": float(arredondar(titulo.valor)),
        "vencimento": titulo.vencimento,
        "data_calculo": hoje,
        "dias_atraso": dias_atraso,
        "juros": float(arredondar(juros)),
        "valor_total": float(arredondar(total)),
    }
