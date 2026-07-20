# tests/test_hash.py

from datetime import date

import pytest

from src.models.produto import Produto
from src.structures.hash_table import HashTable


def criar_produto_teste():
    return Produto(
        codigo_barras="7891234567890",
        nome="Arroz",
        categoria="Alimentos",
        preco=25.90,
        quantidade=10,
        validade=date(2027, 5, 10)
    )


def test_criar_tabela_hash():
    tabela = HashTable(tamanho=10)

    assert tabela.tamanho == 10
    assert tabela.quantidade_elementos == 0
    assert len(tabela) == 0


def test_inserir_produto():
    tabela = HashTable(tamanho=10)
    produto = criar_produto_teste()

    resultado = tabela.inserir(produto)

    assert resultado is True
    assert tabela.quantidade_elementos == 1
    assert len(tabela) == 1


def test_buscar_produto_existente():
    tabela = HashTable(tamanho=10)
    produto = criar_produto_teste()

    tabela.inserir(produto)

    produto_encontrado = tabela.buscar(
        produto.codigo_barras
    )

    assert produto_encontrado is not None
    assert produto_encontrado.codigo_barras == produto.codigo_barras
    assert produto_encontrado.nome == "Arroz"


def test_buscar_produto_inexistente():
    tabela = HashTable(tamanho=10)

    produto_encontrado = tabela.buscar(
        "7890000000000"
    )

    assert produto_encontrado is None
def test_remover_produto_existente():
    tabela = HashTable(tamanho=10)
    produto = criar_produto_teste()

    tabela.inserir(produto)

    produto_removido = tabela.remover(
        produto.codigo_barras
    )

    assert produto_removido is not None
    assert produto_removido.codigo_barras == produto.codigo_barras
    assert tabela.quantidade_elementos == 0
    assert len(tabela) == 0
    assert tabela.buscar(produto.codigo_barras) is None


def test_remover_produto_inexistente():
    tabela = HashTable(tamanho=10)

    produto_removido = tabela.remover(
        "7890000000000"
    )

    assert produto_removido is None
    assert tabela.quantidade_elementos == 0

def test_atualizar_quantidade():
    tabela = HashTable(tamanho=10)
    produto = criar_produto_teste()

    tabela.inserir(produto)

    resultado = tabela.atualizar_quantidade(
        produto.codigo_barras,
        50
    )

    produto_encontrado = tabela.buscar(
        produto.codigo_barras
    )

    assert resultado is True
    assert produto_encontrado is not None
    assert produto_encontrado.quantidade == 50

def test_atualizar_quantidade_de_produto_inexistente():
    tabela = HashTable(tamanho=10)

    resultado = tabela.atualizar_quantidade(
        "7890000000000",
        50
    )

    assert resultado is False

def test_atualizar_quantidade_negativa():
    tabela = HashTable(tamanho=10)
    produto = criar_produto_teste()

    tabela.inserir(produto)

    with pytest.raises(
        ValueError,
        match="A quantidade não pode ser negativa."
    ):
        tabela.atualizar_quantidade(
            produto.codigo_barras,
            -1
        )

def test_atualizar_produto_duplicado():
    tabela = HashTable(tamanho=10)
    produto_original = criar_produto_teste()

    tabela.inserir(produto_original)

    produto_atualizado = Produto(
        codigo_barras=produto_original.codigo_barras,
        nome="Arroz Premium",
        categoria="Alimentos",
        preco=30.90,
        quantidade=25,
        validade=date(2028, 1, 10)
    )

    resultado = tabela.inserir(produto_atualizado)

    produto_encontrado = tabela.buscar(
        produto_original.codigo_barras
    )

    assert resultado is False
    assert tabela.quantidade_elementos == 1
    assert produto_encontrado is not None
    assert produto_encontrado.nome == "Arroz Premium"
    assert produto_encontrado.preco == 30.90
    assert produto_encontrado.quantidade == 25
    assert produto_encontrado.validade == date(2028, 1, 10)

def test_registrar_colisao():
    tabela = HashTable(tamanho=10)

    produto_a = Produto(
        codigo_barras="100",
        nome="Produto A",
        categoria="Teste",
        preco=10.0,
        quantidade=5
    )

    produto_b = Produto(
        codigo_barras="110",
        nome="Produto B",
        categoria="Teste",
        preco=20.0,
        quantidade=8
    )

    tabela.inserir(produto_a)
    tabela.inserir(produto_b)

    assert tabela._funcao_hash("100") == 0
    assert tabela._funcao_hash("110") == 0
    assert tabela.numero_colisoes == 1
    assert tabela.quantidade_elementos == 2
    assert tabela.maior_lista() == 2

def test_listar_produtos():
    tabela = HashTable(tamanho=10)

    produto_a = criar_produto_teste()

    produto_b = Produto(
        codigo_barras="7899876543210",
        nome="Feijão",
        categoria="Alimentos",
        preco=9.90,
        quantidade=15,
        validade=date(2027, 3, 20)
    )

    tabela.inserir(produto_a)
    tabela.inserir(produto_b)

    produtos = tabela.listar_produtos()

    assert len(produtos) == 2
    assert produto_a in produtos
    assert produto_b in produtos

def test_calcular_fator_de_carga():
    tabela = HashTable(tamanho=10)

    produto_a = criar_produto_teste()

    produto_b = Produto(
        codigo_barras="7899876543210",
        nome="Feijão",
        categoria="Alimentos",
        preco=9.90,
        quantidade=15
    )

    tabela.inserir(produto_a)
    tabela.inserir(produto_b)

    assert tabela.fator_carga() == pytest.approx(0.2)

def test_obter_metricas():
    tabela = HashTable(tamanho=10)

    produto_a = Produto(
        codigo_barras="100",
        nome="Produto A",
        categoria="Teste",
        preco=10.0,
        quantidade=5
    )

    produto_b = Produto(
        codigo_barras="110",
        nome="Produto B",
        categoria="Teste",
        preco=20.0,
        quantidade=8
    )

    tabela.inserir(produto_a)
    tabela.inserir(produto_b)

    metricas = tabela.obter_metricas()

    assert metricas["tamanho_tabela"] == 10
    assert metricas["quantidade_elementos"] == 2
    assert metricas["posicoes_ocupadas"] == 1
    assert metricas["fator_carga"] == pytest.approx(0.2)
    assert metricas["numero_colisoes"] == 1
    assert metricas["maior_lista"] == 2

def test_reiniciar_metricas():
    tabela = HashTable(tamanho=10)
    produto = criar_produto_teste()

    tabela.inserir(produto)
    tabela.buscar(produto.codigo_barras)

    assert tabela.numero_comparacoes > 0

    tabela.reiniciar_metricas()

    assert tabela.numero_comparacoes == 0
    assert tabela.numero_colisoes == 0

    # Os produtos continuam armazenados.
    assert tabela.quantidade_elementos == 1