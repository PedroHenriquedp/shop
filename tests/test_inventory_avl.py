# tests/test_inventory_avl.py

from datetime import date

import pytest

from src.inventory.inventory_avl import InventoryAVL
from src.models.produto import Produto


def criar_produto(
    codigo_barras: str = "7891234567890",
    nome: str = "Arroz",
    quantidade: int = 10
) -> Produto:
    return Produto(
        codigo_barras=codigo_barras,
        nome=nome,
        categoria="Alimentos",
        preco=25.90,
        quantidade=quantidade,
        validade=date(2027, 5, 10)
    )


def test_criar_estoque_vazio():
    estoque = InventoryAVL()

    assert len(estoque) == 0


def test_cadastrar_produto():
    estoque = InventoryAVL()
    produto = criar_produto()

    resultado = estoque.cadastrar_produto(produto)

    assert resultado is True
    assert len(estoque) == 1


def test_buscar_produto_existente():
    estoque = InventoryAVL()
    produto = criar_produto()

    estoque.cadastrar_produto(produto)

    produto_encontrado = estoque.buscar_produto(
        produto.codigo_barras
    )

    assert produto_encontrado is not None
    assert produto_encontrado.codigo_barras == produto.codigo_barras
    assert produto_encontrado.nome == "Arroz"


def test_buscar_produto_inexistente():
    estoque = InventoryAVL()

    produto_encontrado = estoque.buscar_produto(
        "7890000000000"
    )

    assert produto_encontrado is None


def test_remover_produto_existente():
    estoque = InventoryAVL()
    produto = criar_produto()

    estoque.cadastrar_produto(produto)

    produto_removido = estoque.remover_produto(
        produto.codigo_barras
    )

    assert produto_removido is not None
    assert produto_removido.codigo_barras == produto.codigo_barras
    assert len(estoque) == 0
    assert estoque.buscar_produto(produto.codigo_barras) is None


def test_remover_produto_inexistente():
    estoque = InventoryAVL()

    produto_removido = estoque.remover_produto(
        "7890000000000"
    )

    assert produto_removido is None
    assert len(estoque) == 0


def test_registrar_entrada():
    estoque = InventoryAVL()
    produto = criar_produto(quantidade=10)

    estoque.cadastrar_produto(produto)

    resultado = estoque.registrar_entrada(
        produto.codigo_barras,
        5
    )

    assert resultado is True
    assert estoque.consultar_quantidade(produto.codigo_barras) == 15


def test_registrar_entrada_produto_inexistente():
    estoque = InventoryAVL()

    resultado = estoque.registrar_entrada(
        "7890000000000",
        5
    )

    assert resultado is False


def test_registrar_entrada_com_quantidade_invalida():
    estoque = InventoryAVL()
    produto = criar_produto()

    estoque.cadastrar_produto(produto)

    with pytest.raises(
        ValueError,
        match="A quantidade de entrada deve ser maior que zero."
    ):
        estoque.registrar_entrada(
            produto.codigo_barras,
            0
        )


def test_registrar_venda():
    estoque = InventoryAVL()
    produto = criar_produto(quantidade=10)

    estoque.cadastrar_produto(produto)

    resultado = estoque.registrar_venda(
        produto.codigo_barras,
        4
    )

    assert resultado is True
    assert estoque.consultar_quantidade(produto.codigo_barras) == 6


def test_registrar_venda_com_estoque_insuficiente():
    estoque = InventoryAVL()
    produto = criar_produto(quantidade=3)

    estoque.cadastrar_produto(produto)

    resultado = estoque.registrar_venda(
        produto.codigo_barras,
        5
    )

    assert resultado is False
    assert estoque.consultar_quantidade(produto.codigo_barras) == 3


def test_registrar_venda_produto_inexistente():
    estoque = InventoryAVL()

    resultado = estoque.registrar_venda(
        "7890000000000",
        2
    )

    assert resultado is False


def test_registrar_venda_com_quantidade_invalida():
    estoque = InventoryAVL()
    produto = criar_produto()

    estoque.cadastrar_produto(produto)

    with pytest.raises(
        ValueError,
        match="A quantidade vendida deve ser maior que zero."
    ):
        estoque.registrar_venda(
            produto.codigo_barras,
            0
        )


def test_atualizar_preco():
    estoque = InventoryAVL()
    produto = criar_produto()

    estoque.cadastrar_produto(produto)

    resultado = estoque.atualizar_preco(
        produto.codigo_barras,
        30.50
    )

    produto_encontrado = estoque.buscar_produto(
        produto.codigo_barras
    )

    assert resultado is True
    assert produto_encontrado is not None
    assert produto_encontrado.preco == 30.50


def test_atualizar_preco_produto_inexistente():
    estoque = InventoryAVL()

    resultado = estoque.atualizar_preco(
        "7890000000000",
        30.50
    )

    assert resultado is False


def test_atualizar_preco_negativo():
    estoque = InventoryAVL()
    produto = criar_produto()

    estoque.cadastrar_produto(produto)

    with pytest.raises(
        ValueError,
        match="O preço não pode ser negativo."
    ):
        estoque.atualizar_preco(
            produto.codigo_barras,
            -1
        )


def test_consultar_quantidade_produto_inexistente():
    estoque = InventoryAVL()

    quantidade = estoque.consultar_quantidade(
        "7890000000000"
    )

    assert quantidade is None


def test_listar_produtos():
    estoque = InventoryAVL()

    produto_a = criar_produto(
        codigo_barras="100",
        nome="Arroz"
    )

    produto_b = criar_produto(
        codigo_barras="200",
        nome="Feijão"
    )

    estoque.cadastrar_produto(produto_a)
    estoque.cadastrar_produto(produto_b)

    produtos = estoque.listar_produtos()

    assert len(produtos) == 2
    assert produto_a in produtos
    assert produto_b in produtos


def test_listar_produtos_em_ordem_de_codigo():
    estoque = InventoryAVL()

    estoque.cadastrar_produto(
        criar_produto("300", "Macarrão")
    )

    estoque.cadastrar_produto(
        criar_produto("100", "Arroz")
    )

    estoque.cadastrar_produto(
        criar_produto("200", "Feijão")
    )

    produtos = estoque.listar_produtos()

    codigos = [
        produto.codigo_barras
        for produto in produtos
    ]

    assert codigos == ["100", "200", "300"]


def test_listar_produtos_por_nome():
    estoque = InventoryAVL()

    estoque.cadastrar_produto(
        criar_produto("100", "Feijão")
    )

    estoque.cadastrar_produto(
        criar_produto("200", "Arroz")
    )

    estoque.cadastrar_produto(
        criar_produto("300", "Macarrão")
    )

    produtos = estoque.listar_produtos_por_nome()

    nomes = [
        produto.nome
        for produto in produtos
    ]

    assert nomes == ["Arroz", "Feijão", "Macarrão"]


def test_listar_produtos_por_validade():
    estoque = InventoryAVL()

    produto_a = Produto(
        codigo_barras="100",
        nome="Produto A",
        categoria="Teste",
        preco=10.0,
        quantidade=5,
        validade=date(2027, 5, 10)
    )

    produto_b = Produto(
        codigo_barras="200",
        nome="Produto B",
        categoria="Teste",
        preco=10.0,
        quantidade=5,
        validade=date(2026, 1, 10)
    )

    produto_c = Produto(
        codigo_barras="300",
        nome="Produto C",
        categoria="Teste",
        preco=10.0,
        quantidade=5,
        validade=None
    )

    estoque.cadastrar_produto(produto_a)
    estoque.cadastrar_produto(produto_b)
    estoque.cadastrar_produto(produto_c)

    produtos = estoque.listar_produtos_por_validade()

    codigos = [
        produto.codigo_barras
        for produto in produtos
    ]

    assert codigos == ["200", "100", "300"]


def test_atualizar_produto_duplicado():
    estoque = InventoryAVL()

    produto_original = criar_produto(
        codigo_barras="200",
        nome="Produto Original",
        quantidade=10
    )

    estoque.cadastrar_produto(produto_original)

    produto_atualizado = Produto(
        codigo_barras="200",
        nome="Produto Atualizado",
        categoria="Nova categoria",
        preco=35.90,
        quantidade=30,
        validade=date(2028, 5, 10)
    )

    resultado = estoque.cadastrar_produto(
        produto_atualizado
    )

    produto_encontrado = estoque.buscar_produto("200")

    assert resultado is False
    assert len(estoque) == 1

    assert produto_encontrado is not None
    assert produto_encontrado.nome == "Produto Atualizado"
    assert produto_encontrado.categoria == "Nova categoria"
    assert produto_encontrado.preco == 35.90
    assert produto_encontrado.quantidade == 30
    assert produto_encontrado.validade == date(2028, 5, 10)


def test_obter_metricas():
    estoque = InventoryAVL()

    estoque.cadastrar_produto(
        criar_produto("300", "Produto A")
    )

    estoque.cadastrar_produto(
        criar_produto("200", "Produto B")
    )

    estoque.cadastrar_produto(
        criar_produto("100", "Produto C")
    )

    metricas = estoque.obter_metricas()

    assert metricas["quantidade_elementos"] == 3
    assert metricas["altura_arvore"] == 2
    assert metricas["numero_comparacoes"] > 0
    assert metricas["numero_rotacoes"] == 1


def test_reiniciar_metricas():
    estoque = InventoryAVL()

    estoque.cadastrar_produto(
        criar_produto("300")
    )

    estoque.cadastrar_produto(
        criar_produto("200")
    )

    estoque.cadastrar_produto(
        criar_produto("100")
    )

    assert estoque.obter_metricas()["numero_comparacoes"] > 0
    assert estoque.obter_metricas()["numero_rotacoes"] > 0

    estoque.reiniciar_metricas()

    metricas = estoque.obter_metricas()

    assert metricas["numero_comparacoes"] == 0
    assert metricas["numero_rotacoes"] == 0

    # Os produtos continuam armazenados.
    assert len(estoque) == 3