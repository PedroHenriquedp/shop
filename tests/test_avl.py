# tests/test_avl.py

from datetime import date

from src.models.produto import Produto
from src.structures.avl_tree import AVLTree


def criar_produto(
    codigo_barras: str,
    nome: str = "Produto"
) -> Produto:
    return Produto(
        codigo_barras=codigo_barras,
        nome=nome,
        categoria="Teste",
        preco=10.0,
        quantidade=5,
        validade=date(2027, 1, 1)
    )


def test_criar_arvore_vazia():
    arvore = AVLTree()

    assert arvore.raiz is None
    assert arvore.quantidade_elementos == 0
    assert len(arvore) == 0
    assert arvore.obter_altura() == 0


def test_inserir_produto():
    arvore = AVLTree()
    produto = criar_produto("200", "Produto A")

    resultado = arvore.inserir(produto)

    assert resultado is True
    assert arvore.raiz is not None
    assert arvore.raiz.produto.codigo_barras == "200"
    assert arvore.quantidade_elementos == 1
    assert len(arvore) == 1
    assert arvore.obter_altura() == 1


def test_buscar_produto_existente():
    arvore = AVLTree()
    produto = criar_produto("200", "Produto A")

    arvore.inserir(produto)

    produto_encontrado = arvore.buscar("200")

    assert produto_encontrado is not None
    assert produto_encontrado.codigo_barras == "200"
    assert produto_encontrado.nome == "Produto A"


def test_buscar_produto_inexistente():
    arvore = AVLTree()

    produto_encontrado = arvore.buscar("999")

    assert produto_encontrado is None


def test_inserir_varios_produtos():
    arvore = AVLTree()

    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("100"))
    arvore.inserir(criar_produto("300"))

    assert arvore.quantidade_elementos == 3
    assert len(arvore) == 3

    assert arvore.buscar("100") is not None
    assert arvore.buscar("200") is not None
    assert arvore.buscar("300") is not None


def test_listar_produtos_em_ordem():
    arvore = AVLTree()

    arvore.inserir(criar_produto("300"))
    arvore.inserir(criar_produto("100"))
    arvore.inserir(criar_produto("200"))

    produtos = arvore.listar_em_ordem()

    codigos = [
        produto.codigo_barras
        for produto in produtos
    ]

    assert codigos == ["100", "200", "300"]


def test_verificar_produto_com_contains():
    arvore = AVLTree()

    arvore.inserir(criar_produto("200"))

    assert "200" in arvore
    assert "999" not in arvore

def test_rotacao_simples_direita():
    arvore = AVLTree()

    arvore.inserir(criar_produto("300"))
    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("100"))

    assert arvore.raiz is not None
    assert arvore.raiz.produto.codigo_barras == "200"

    assert arvore.raiz.esquerda is not None
    assert arvore.raiz.esquerda.produto.codigo_barras == "100"

    assert arvore.raiz.direita is not None
    assert arvore.raiz.direita.produto.codigo_barras == "300"

    assert arvore.numero_rotacoes == 1


def test_rotacao_simples_esquerda():
    arvore = AVLTree()

    arvore.inserir(criar_produto("100"))
    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("300"))

    assert arvore.raiz is not None
    assert arvore.raiz.produto.codigo_barras == "200"

    assert arvore.raiz.esquerda is not None
    assert arvore.raiz.esquerda.produto.codigo_barras == "100"

    assert arvore.raiz.direita is not None
    assert arvore.raiz.direita.produto.codigo_barras == "300"

    assert arvore.numero_rotacoes == 1


def test_rotacao_dupla_esquerda_direita():
    arvore = AVLTree()

    arvore.inserir(criar_produto("300"))
    arvore.inserir(criar_produto("100"))
    arvore.inserir(criar_produto("200"))

    assert arvore.raiz is not None
    assert arvore.raiz.produto.codigo_barras == "200"

    assert arvore.raiz.esquerda is not None
    assert arvore.raiz.esquerda.produto.codigo_barras == "100"

    assert arvore.raiz.direita is not None
    assert arvore.raiz.direita.produto.codigo_barras == "300"

    assert arvore.numero_rotacoes == 2


def test_rotacao_dupla_direita_esquerda():
    arvore = AVLTree()

    arvore.inserir(criar_produto("100"))
    arvore.inserir(criar_produto("300"))
    arvore.inserir(criar_produto("200"))

    assert arvore.raiz is not None
    assert arvore.raiz.produto.codigo_barras == "200"

    assert arvore.raiz.esquerda is not None
    assert arvore.raiz.esquerda.produto.codigo_barras == "100"

    assert arvore.raiz.direita is not None
    assert arvore.raiz.direita.produto.codigo_barras == "300"

    assert arvore.numero_rotacoes == 2


def test_atualizar_produto_duplicado():
    arvore = AVLTree()

    produto_original = criar_produto(
        codigo_barras="200",
        nome="Produto Original"
    )

    arvore.inserir(produto_original)

    produto_atualizado = Produto(
        codigo_barras="200",
        nome="Produto Atualizado",
        categoria="Nova categoria",
        preco=25.90,
        quantidade=30,
        validade=date(2028, 5, 10)
    )

    resultado = arvore.inserir(produto_atualizado)

    produto_encontrado = arvore.buscar("200")

    assert resultado is False
    assert arvore.quantidade_elementos == 1
    assert len(arvore) == 1

    assert produto_encontrado is not None
    assert produto_encontrado.nome == "Produto Atualizado"
    assert produto_encontrado.categoria == "Nova categoria"
    assert produto_encontrado.preco == 25.90
    assert produto_encontrado.quantidade == 30
    assert produto_encontrado.validade == date(2028, 5, 10)


def test_obter_metricas():
    arvore = AVLTree()

    arvore.inserir(criar_produto("300"))
    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("100"))

    metricas = arvore.obter_metricas()

    assert metricas["quantidade_elementos"] == 3
    assert metricas["altura_arvore"] == 2
    assert metricas["numero_comparacoes"] > 0
    assert metricas["numero_rotacoes"] == 1


def test_reiniciar_metricas():
    arvore = AVLTree()

    arvore.inserir(criar_produto("300"))
    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("100"))

    arvore.buscar("200")

    assert arvore.numero_comparacoes > 0
    assert arvore.numero_rotacoes > 0

    arvore.reiniciar_metricas()

    assert arvore.numero_comparacoes == 0
    assert arvore.numero_rotacoes == 0

    # A estrutura continua intacta.
    assert arvore.quantidade_elementos == 3
    assert arvore.buscar("200") is not None


def test_altura_de_arvore_balanceada():
    arvore = AVLTree()

    codigos = [
        "100",
        "200",
        "300",
        "400",
        "500",
        "600",
        "700"
    ]

    for codigo in codigos:
        arvore.inserir(criar_produto(codigo))

    assert arvore.quantidade_elementos == 7

    # Para 7 elementos, uma AVL bem balanceada deve ter altura pequena.
    assert arvore.obter_altura() <= 3


def test_listagem_permanece_ordenada_apos_rotacoes():
    arvore = AVLTree()

    codigos = [
        "500",
        "300",
        "700",
        "200",
        "400",
        "600",
        "800",
        "100"
    ]

    for codigo in codigos:
        arvore.inserir(criar_produto(codigo))

    produtos = arvore.listar_em_ordem()

    codigos_ordenados = [
        produto.codigo_barras
        for produto in produtos
    ]

    assert codigos_ordenados == sorted(codigos)


def test_fator_de_balanceamento_da_raiz():
    arvore = AVLTree()

    arvore.inserir(criar_produto("100"))
    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("300"))
    arvore.inserir(criar_produto("400"))
    arvore.inserir(criar_produto("500"))

    assert arvore.raiz is not None

    fator = arvore._fator_balanceamento(arvore.raiz)

    assert -1 <= fator <= 1

def test_remover_no_folha():
    arvore = AVLTree()

    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("100"))
    arvore.inserir(criar_produto("300"))

    produto_removido = arvore.remover("100")

    assert produto_removido is not None
    assert produto_removido.codigo_barras == "100"

    assert arvore.buscar("100") is None
    assert arvore.quantidade_elementos == 2
    assert len(arvore) == 2

    produtos = arvore.listar_em_ordem()
    codigos = [produto.codigo_barras for produto in produtos]

    assert codigos == ["200", "300"]


def test_remover_no_com_um_filho():
    arvore = AVLTree()

    arvore.inserir(criar_produto("300"))
    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("400"))
    arvore.inserir(criar_produto("100"))

    produto_removido = arvore.remover("200")

    assert produto_removido is not None
    assert produto_removido.codigo_barras == "200"

    assert arvore.buscar("200") is None
    assert arvore.buscar("100") is not None
    assert arvore.quantidade_elementos == 3

    produtos = arvore.listar_em_ordem()
    codigos = [produto.codigo_barras for produto in produtos]

    assert codigos == ["100", "300", "400"]


def test_remover_no_com_dois_filhos():
    arvore = AVLTree()

    arvore.inserir(criar_produto("400"))
    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("600"))
    arvore.inserir(criar_produto("100"))
    arvore.inserir(criar_produto("300"))
    arvore.inserir(criar_produto("500"))
    arvore.inserir(criar_produto("700"))

    produto_removido = arvore.remover("400")

    assert produto_removido is not None
    assert produto_removido.codigo_barras == "400"

    assert arvore.buscar("400") is None
    assert arvore.quantidade_elementos == 6

    produtos = arvore.listar_em_ordem()
    codigos = [produto.codigo_barras for produto in produtos]

    assert codigos == [
        "100",
        "200",
        "300",
        "500",
        "600",
        "700"
    ]


def test_remover_raiz_com_um_unico_no():
    arvore = AVLTree()

    arvore.inserir(criar_produto("200"))

    produto_removido = arvore.remover("200")

    assert produto_removido is not None
    assert produto_removido.codigo_barras == "200"

    assert arvore.raiz is None
    assert arvore.quantidade_elementos == 0
    assert len(arvore) == 0
    assert arvore.obter_altura() == 0


def test_remover_raiz_com_um_filho():
    arvore = AVLTree()

    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("100"))

    produto_removido = arvore.remover("200")

    assert produto_removido is not None
    assert produto_removido.codigo_barras == "200"

    assert arvore.raiz is not None
    assert arvore.raiz.produto.codigo_barras == "100"

    assert arvore.quantidade_elementos == 1
    assert arvore.buscar("200") is None
    assert arvore.buscar("100") is not None


def test_remover_produto_inexistente():
    arvore = AVLTree()

    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("100"))
    arvore.inserir(criar_produto("300"))

    produto_removido = arvore.remover("999")

    assert produto_removido is None

    assert arvore.quantidade_elementos == 3
    assert len(arvore) == 3

    produtos = arvore.listar_em_ordem()
    codigos = [produto.codigo_barras for produto in produtos]

    assert codigos == ["100", "200", "300"]


def test_remover_em_arvore_vazia():
    arvore = AVLTree()

    produto_removido = arvore.remover("200")

    assert produto_removido is None
    assert arvore.raiz is None
    assert arvore.quantidade_elementos == 0


def test_remover_varios_produtos():
    arvore = AVLTree()

    codigos = [
        "400",
        "200",
        "600",
        "100",
        "300",
        "500",
        "700"
    ]

    for codigo in codigos:
        arvore.inserir(criar_produto(codigo))

    assert arvore.quantidade_elementos == 7

    arvore.remover("100")
    arvore.remover("600")
    arvore.remover("400")

    assert arvore.quantidade_elementos == 4

    produtos = arvore.listar_em_ordem()
    codigos_restantes = [
        produto.codigo_barras
        for produto in produtos
    ]

    assert codigos_restantes == [
        "200",
        "300",
        "500",
        "700"
    ]


def test_arvore_permanece_ordenada_apos_remocao():
    arvore = AVLTree()

    codigos = [
        "500",
        "300",
        "700",
        "200",
        "400",
        "600",
        "800",
        "100"
    ]

    for codigo in codigos:
        arvore.inserir(criar_produto(codigo))

    arvore.remover("300")
    arvore.remover("700")

    produtos = arvore.listar_em_ordem()

    codigos_resultantes = [
        produto.codigo_barras
        for produto in produtos
    ]

    assert codigos_resultantes == sorted(
        ["500", "200", "400", "600", "800", "100"]
    )


def test_balanceamento_apos_remocao():
    arvore = AVLTree()

    codigos = [
        "400",
        "200",
        "600",
        "100",
        "300",
        "500",
        "700",
        "050"
    ]

    for codigo in codigos:
        arvore.inserir(criar_produto(codigo))

    arvore.remover("700")
    arvore.remover("600")

    assert arvore.raiz is not None

    fator_raiz = arvore._fator_balanceamento(
        arvore.raiz
    )

    assert -1 <= fator_raiz <= 1


def test_rotacao_apos_remocao():
    arvore = AVLTree()

    arvore.inserir(criar_produto("300"))
    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("400"))
    arvore.inserir(criar_produto("100"))

    arvore.reiniciar_metricas()

    produto_removido = arvore.remover("400")

    assert produto_removido is not None
    assert produto_removido.codigo_barras == "400"

    assert arvore.raiz is not None
    assert arvore.raiz.produto.codigo_barras == "200"

    assert arvore.raiz.esquerda is not None
    assert arvore.raiz.esquerda.produto.codigo_barras == "100"

    assert arvore.raiz.direita is not None
    assert arvore.raiz.direita.produto.codigo_barras == "300"

    assert arvore.numero_rotacoes == 1


def test_alturas_atualizadas_apos_remocao():
    arvore = AVLTree()

    arvore.inserir(criar_produto("400"))
    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("600"))
    arvore.inserir(criar_produto("100"))
    arvore.inserir(criar_produto("300"))

    altura_antes = arvore.obter_altura()

    arvore.remover("100")
    arvore.remover("300")

    altura_depois = arvore.obter_altura()

    assert altura_antes == 3
    assert altura_depois == 2


def test_remocao_atualiza_metricas():
    arvore = AVLTree()

    arvore.inserir(criar_produto("200"))
    arvore.inserir(criar_produto("100"))
    arvore.inserir(criar_produto("300"))

    arvore.reiniciar_metricas()

    arvore.remover("100")

    metricas = arvore.obter_metricas()

    assert metricas["quantidade_elementos"] == 2
    assert metricas["numero_comparacoes"] > 0
    assert metricas["altura_arvore"] == 2