# tests/test_produto.py

from datetime import date

import pytest

from src.models.produto import Produto


def test_criar_produto_valido():
    produto = Produto(
        codigo_barras="7891234567890",
        nome="Arroz Tipo 1",
        categoria="Alimentos",
        preco=25.90,
        quantidade=20,
        validade=date(2027, 5, 10)
    )

    assert produto.codigo_barras == "7891234567890"
    assert produto.nome == "Arroz Tipo 1"
    assert produto.categoria == "Alimentos"
    assert produto.preco == 25.90
    assert produto.quantidade == 20
    assert produto.validade == date(2027, 5, 10)


def test_criar_produto_sem_validade():
    produto = Produto(
        codigo_barras="7891234567890",
        nome="Sal",
        categoria="Alimentos",
        preco=3.50,
        quantidade=10
    )

    assert produto.validade is None


def test_codigo_de_barras_com_letras():
    with pytest.raises(
        ValueError,
        match="O código de barras deve conter apenas números."
    ):
        Produto(
            codigo_barras="789ABC4567890",
            nome="Produto Inválido",
            categoria="Teste",
            preco=10.00,
            quantidade=5
        )


def test_nome_vazio():
    with pytest.raises(
        ValueError,
        match="O nome não pode ser vazio."
    ):
        Produto(
            codigo_barras="7891234567890",
            nome="",
            categoria="Alimentos",
            preco=10.00,
            quantidade=5
        )


def test_categoria_vazia():
    with pytest.raises(
        ValueError,
        match="A categoria não pode ser vazia."
    ):
        Produto(
            codigo_barras="7891234567890",
            nome="Arroz",
            categoria="",
            preco=10.00,
            quantidade=5
        )


def test_preco_negativo():
    with pytest.raises(
        ValueError,
        match="O preço não pode ser negativo."
    ):
        Produto(
            codigo_barras="7891234567890",
            nome="Arroz",
            categoria="Alimentos",
            preco=-10.00,
            quantidade=5
        )


def test_quantidade_negativa():
    with pytest.raises(
        ValueError,
        match="A quantidade não pode ser negativa."
    ):
        Produto(
            codigo_barras="7891234567890",
            nome="Arroz",
            categoria="Alimentos",
            preco=10.00,
            quantidade=-5
        )