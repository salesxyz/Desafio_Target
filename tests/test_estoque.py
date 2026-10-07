import pytest
from exercicio2 import estoque


@pytest.fixture
def dados():
    # dados só em memória, os testes não mexem no estoque.json de verdade
    return {
        "estoque": [
            {"codigoProduto": 101, "descricaoProduto": "Caneta Azul", "estoque": 150},
            {"codigoProduto": 102, "descricaoProduto": "Caderno Universitário", "estoque": 75},
        ],
        "movimentacoes": [],
    }


def test_entrada_aumenta_o_estoque(dados):
    mov = estoque.registrar_movimentacao(dados, 101, "entrada", 50, "Compra de fornecedor")

    assert mov["saldoAnterior"] == 150
    assert mov["saldoFinal"] == 200
    assert dados["estoque"][0]["estoque"] == 200
    assert mov["descricao"] == "Compra de fornecedor"


def test_saida_diminui_o_estoque(dados):
    mov = estoque.registrar_movimentacao(dados, 102, "saida", 25, "Venda")

    assert mov["saldoFinal"] == 50
    assert dados["estoque"][1]["estoque"] == 50


def test_saida_de_todo_o_estoque_e_permitida(dados):
    mov = estoque.registrar_movimentacao(dados, 102, "saida", 75, "Venda")
    assert mov["saldoFinal"] == 0


def test_ids_sao_unicos_e_sequenciais(dados):
    m1 = estoque.registrar_movimentacao(dados, 101, "entrada", 1, "Compra de fornecedor")
    m2 = estoque.registrar_movimentacao(dados, 101, "saida", 1, "Venda")
    m3 = estoque.registrar_movimentacao(dados, 102, "entrada", 1, "Compra de fornecedor")

    assert [m1["id"], m2["id"], m3["id"]] == [1, 2, 3]
    assert len(dados["movimentacoes"]) == 3


def test_id_continua_do_maior_id_existente(dados):
    dados["movimentacoes"].append({"id": 7})
    assert estoque.gerar_id(dados) == 8


def test_saida_maior_que_o_saldo_nao_altera_nada(dados):
    with pytest.raises(ValueError, match="Estoque insuficiente"):
        estoque.registrar_movimentacao(dados, 102, "saida", 80, "Venda")

    assert dados["estoque"][1]["estoque"] == 75
    assert dados["movimentacoes"] == []


@pytest.mark.parametrize("quantidade", [0, -5])
def test_quantidade_invalida(dados, quantidade):
    with pytest.raises(ValueError):
        estoque.registrar_movimentacao(dados, 101, "entrada", quantidade, "Compra de fornecedor")
    assert dados["movimentacoes"] == []


def test_produto_inexistente(dados):
    with pytest.raises(ValueError, match="não encontrado"):
        estoque.registrar_movimentacao(dados, 999, "entrada", 1, "Compra de fornecedor")


def test_tipo_invalido(dados):
    with pytest.raises(ValueError, match="Tipo"):
        estoque.registrar_movimentacao(dados, 101, "transferencia", 1, "Teste")


def test_salvar_e_carregar(dados, tmp_path, monkeypatch):
    monkeypatch.setattr(estoque, "arquivo", str(tmp_path / "estoque.json"))

    estoque.registrar_movimentacao(dados, 101, "entrada", 10, "Compra de fornecedor")
    estoque.salvar(dados)
    lidos = estoque.carregar()

    assert lidos["estoque"][0]["estoque"] == 160
    assert len(lidos["movimentacoes"]) == 1


def test_carregar_sem_arquivo_comeca_vazio(tmp_path, monkeypatch):
    monkeypatch.setattr(estoque, "arquivo", str(tmp_path / "nao_existe.json"))

    dados = estoque.carregar()

    assert dados == {"estoque": [], "movimentacoes": []}
