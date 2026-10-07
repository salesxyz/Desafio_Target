# Desafio Dev

Resolução dos três exercícios do desafio, feita em Python.

## Requisitos

- Python 3.9 ou superior
- Exercícios 1 e 2: só a biblioteca padrão, não precisa instalar nada
- Exercício 3: FastAPI e Uvicorn
- Testes: pytest e httpx

## Estrutura

```
.
├── exercicio1/
│   ├── comissao.py
│   └── vendas.json
├── exercicio2/
│   ├── estoque.py
│   └── estoque.json
├── exercicio3/
│   └── juros.py
├── tests/
│   ├── test_comissao.py
│   ├── test_estoque.py
│   └── test_juros.py
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Preparando o ambiente

```
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / Mac

pip install -r requirements-dev.txt
```

Para só rodar o exercício 3, sem os testes, basta `pip install -r requirements.txt`.

---

## Exercício 1 - Comissão por vendedor

Lê o `vendas.json` e calcula a comissão de cada vendedor.

```
cd exercicio1
python comissao.py
```

**Regra aplicada a cada venda**

| Valor da venda | Comissão |
|---|---|
| menor que R$ 100,00 | não gera |
| de R$ 100,00 até R$ 499,99 | 1% |
| a partir de R$ 500,00 | 5% |

**Resultado**

| Vendedor | Comissão |
|---|---|
| Ana Lima | R$ 404,98 |
| Carlos Oliveira | R$ 379,37 |
| João Silva | R$ 495,68 |
| Maria Souza | R$ 465,95 |

**Decisões**

- A regra é aplicada em cada venda e depois somada por vendedor. Não é aplicada em cima do total.
- As bordas seguem o enunciado: R$ 100,00 já gera 1% e R$ 500,00 já gera 5% ("a partir de").
- Usei `Decimal` em vez de `float` para não ter erro de arredondamento nos centavos.

---

## Exercício 2 - Movimentação de estoque

Programa de console para lançar entradas e saídas dos produtos do `estoque.json`.

```
cd exercicio2
python estoque.py
```

**Menu**

```
1 - Entrada
2 - Saída
3 - Ver estoque
4 - Ver movimentações
0 - Sair
```

Em cada lançamento o programa pede o código do produto, a quantidade e a descrição (escolhida de uma lista). No final mostra o estoque final do produto, por exemplo:

```
Movimentação 2 registrada: Perda/avaria
Estoque final de Caderno Universitário: 50
```

**Descrições disponíveis**

- Entrada: Compra de fornecedor, Devolução de cliente, Ajuste de inventário
- Saída: Venda, Perda/avaria, Ajuste de inventário

**Como os dados são salvos**

O próprio `estoque.json` é atualizado a cada lançamento. Ele guarda os saldos dos produtos e uma lista `movimentacoes`, onde cada item tem:

```json
{
  "id": 1,
  "data": "07/10/2026 01:22:04",
  "codigoProduto": 101,
  "tipo": "entrada",
  "descricao": "Compra de fornecedor",
  "quantidade": 50,
  "saldoAnterior": 150,
  "saldoFinal": 200
}
```

**Decisões**

- O ID é sequencial: o maior ID que já existe no histórico + 1. Continua de onde parou mesmo depois de fechar o programa.
- A regra de negócio fica na função `registrar_movimentacao`, separada de `input` e `print`, para dar para testar.
- Não deixa lançar produto que não existe, quantidade zero ou negativa, nem texto no lugar de número.
- Não deixa a saída ser maior que o saldo, para o estoque nunca ficar negativo. Quando dá erro, nada é alterado.
- Guardei o histórico completo (e não só o saldo) para dar para conferir cada movimentação depois.

---

## Exercício 3 - Juros por atraso

API feita com FastAPI que calcula os juros de um valor vencido, até a data de hoje.

```
cd exercicio3
uvicorn juros:app --reload
```

Depois abra `http://127.0.0.1:8000/docs` no navegador. O FastAPI cria essa página sozinho e dá para testar o endpoint por lá, clicando em "Try it out".

**Endpoint**

`POST /juros`

```json
{
  "valor": 1000,
  "vencimento": "2026-09-27"
}
```

O vencimento vai no formato `AAAA-MM-DD`.

**Resposta** (exemplo calculado em 07/10/2026)

```json
{
  "valor_original": 1000.0,
  "vencimento": "2026-09-27",
  "data_calculo": "2026-10-07",
  "dias_atraso": 10,
  "juros": 250.0,
  "valor_total": 1250.0
}
```

Também dá para chamar pelo PowerShell:

```
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/juros -ContentType "application/json" -Body '{"valor": 1000, "vencimento": "2026-09-27"}'
```

**Decisões**

- O enunciado fala em "juros", mas descreve uma "multa de 2,5% ao dia". Interpretei como juros simples: `valor × 2,5% × dias de atraso`. Se fosse juros compostos, bastaria trocar essa conta.
- Se a data de vencimento ainda não passou (ou é hoje), os dias de atraso são 0 e não tem juros.
- Valor igual ou menor que zero e data em formato errado retornam erro 422 com a explicação.
- Valores com `Decimal` e arredondados para centavos.

---

## Testes

Na raiz do projeto, com o ambiente virtual ativado:

```
pytest
```

Os testes cobrem as bordas das faixas de comissão (99,99, 100, 499,99 e 500), o resultado com o JSON do desafio, as regras do estoque (saldo insuficiente, quantidade inválida, IDs únicos, salvar e carregar) e o cálculo de juros, tanto na função quanto no endpoint. Eles não alteram o `estoque.json`.
