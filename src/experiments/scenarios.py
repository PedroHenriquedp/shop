# src/experiments/scenarios.py

import random
from dataclasses import dataclass

from src.models.produto import Produto


@dataclass
class OperacaoVenda:
    codigo_barras: str
    quantidade: int


@dataclass
class OperacaoMista:
    tipo: str
    codigo_barras: str
    quantidade: int | None = None


@dataclass
class CenariosExperimento:
    """
    Agrupa as operações que serão executadas durante os experimentos.
    """

    codigos_busca_existente: list[str]
    codigos_busca_inexistente: list[str]
    codigos_remocao: list[str]
    vendas: list[OperacaoVenda]
    operacoes_mistas: list[OperacaoMista]


def selecionar_codigos_existentes(
    produtos: list[Produto],
    quantidade: int,
    seed: int = 42
) -> list[str]:
    """
    Seleciona códigos de barras existentes de forma reproduzível.

    Caso a quantidade solicitada seja maior que o número de produtos,
    os códigos poderão se repetir.
    """
    if quantidade < 0:
        raise ValueError(
            "A quantidade de buscas não pode ser negativa."
        )

    if not produtos and quantidade > 0:
        raise ValueError(
            "Não é possível selecionar códigos de uma lista vazia."
        )

    gerador = random.Random(seed)

    codigos = [
        produto.codigo_barras
        for produto in produtos
    ]

    if quantidade <= len(codigos):
        return gerador.sample(
            codigos,
            quantidade
        )

    return [
        gerador.choice(codigos)
        for _ in range(quantidade)
    ]


def gerar_codigos_inexistentes(
    produtos: list[Produto],
    quantidade: int,
    seed: int = 42
) -> list[str]:
    """
    Gera códigos numéricos que não existem na base de produtos.
    """
    if quantidade < 0:
        raise ValueError(
            "A quantidade de códigos não pode ser negativa."
        )

    gerador = random.Random(seed)

    codigos_existentes = {
        produto.codigo_barras
        for produto in produtos
    }

    codigos_gerados: set[str] = set()

    while len(codigos_gerados) < quantidade:
        codigo = str(
            gerador.randint(
                10_000_000_000_000,
                99_999_999_999_999
            )
        )

        if (
            codigo not in codigos_existentes
            and codigo not in codigos_gerados
        ):
            codigos_gerados.add(codigo)

    return list(codigos_gerados)


def selecionar_codigos_remocao(
    produtos: list[Produto],
    percentual: float = 0.10,
    seed: int = 42
) -> list[str]:
    """
    Seleciona uma parcela dos produtos para remoção.

    Por padrão, seleciona 10% da base.
    """
    if percentual < 0 or percentual > 1:
        raise ValueError(
            "O percentual deve estar entre 0 e 1."
        )

    if not produtos:
        return []

    quantidade = max(
        1,
        int(len(produtos) * percentual)
    )

    gerador = random.Random(seed)

    codigos = [
        produto.codigo_barras
        for produto in produtos
    ]

    return gerador.sample(
        codigos,
        min(quantidade, len(codigos))
    )


def gerar_vendas(
    produtos: list[Produto],
    quantidade_operacoes: int,
    quantidade_maxima_por_venda: int = 3,
    seed: int = 42
) -> list[OperacaoVenda]:
    """
    Gera operações de venda para produtos existentes.

    A quantidade vendida é limitada ao estoque disponível
    de cada produto no momento da geração.
    """
    if quantidade_operacoes < 0:
        raise ValueError(
            "A quantidade de operações não pode ser negativa."
        )

    if quantidade_maxima_por_venda <= 0:
        raise ValueError(
            "A quantidade máxima por venda deve ser maior que zero."
        )

    produtos_disponiveis = [
        produto
        for produto in produtos
        if produto.quantidade > 0
    ]

    if not produtos_disponiveis and quantidade_operacoes > 0:
        raise ValueError(
            "Não existem produtos com estoque disponível."
        )

    gerador = random.Random(seed)

    vendas: list[OperacaoVenda] = []

    for _ in range(quantidade_operacoes):
        produto = gerador.choice(
            produtos_disponiveis
        )

        limite = min(
            produto.quantidade,
            quantidade_maxima_por_venda
        )

        quantidade = gerador.randint(
            1,
            limite
        )

        vendas.append(
            OperacaoVenda(
                codigo_barras=produto.codigo_barras,
                quantidade=quantidade
            )
        )

    return vendas


def gerar_operacoes_mistas(
    produtos: list[Produto],
    quantidade_operacoes: int,
    seed: int = 42
) -> list[OperacaoMista]:
    """
    Gera uma sequência mista de operações.

    Distribuição aproximada:
    - 50% buscas;
    - 25% vendas;
    - 15% entradas;
    - 10% atualizações de preço.
    """
    if quantidade_operacoes < 0:
        raise ValueError(
            "A quantidade de operações não pode ser negativa."
        )

    if not produtos and quantidade_operacoes > 0:
        raise ValueError(
            "Não é possível gerar operações para uma lista vazia."
        )

    gerador = random.Random(seed)

    operacoes: list[OperacaoMista] = []

    for _ in range(quantidade_operacoes):
        produto = gerador.choice(produtos)
        sorteio = gerador.random()

        if sorteio < 0.50:
            operacoes.append(
                OperacaoMista(
                    tipo="busca",
                    codigo_barras=produto.codigo_barras
                )
            )

        elif sorteio < 0.75:
            quantidade_venda = min(
                produto.quantidade,
                gerador.randint(1, 3)
            )

            if quantidade_venda <= 0:
                quantidade_venda = 1

            operacoes.append(
                OperacaoMista(
                    tipo="venda",
                    codigo_barras=produto.codigo_barras,
                    quantidade=quantidade_venda
                )
            )

        elif sorteio < 0.90:
            operacoes.append(
                OperacaoMista(
                    tipo="entrada",
                    codigo_barras=produto.codigo_barras,
                    quantidade=gerador.randint(1, 5)
                )
            )

        else:
            novo_preco_centavos = gerador.randint(
                100,
                50_000
            )

            operacoes.append(
                OperacaoMista(
                    tipo="atualizacao_preco",
                    codigo_barras=produto.codigo_barras,
                    quantidade=novo_preco_centavos
                )
            )

    return operacoes


def criar_cenarios(
    produtos: list[Produto],
    seed: int = 42
) -> CenariosExperimento:
    """
    Cria todos os cenários usados no benchmark.

    A quantidade de operações é baseada no tamanho da base.
    """
    tamanho_base = len(produtos)

    codigos_busca_existente = selecionar_codigos_existentes(
        produtos=produtos,
        quantidade=tamanho_base,
        seed=seed
    )

    codigos_busca_inexistente = gerar_codigos_inexistentes(
        produtos=produtos,
        quantidade=tamanho_base,
        seed=seed + 1
    )

    codigos_remocao = selecionar_codigos_remocao(
        produtos=produtos,
        percentual=0.10,
        seed=seed + 2
    )

    vendas = gerar_vendas(
        produtos=produtos,
        quantidade_operacoes=tamanho_base,
        quantidade_maxima_por_venda=3,
        seed=seed + 3
    )

    operacoes_mistas = gerar_operacoes_mistas(
        produtos=produtos,
        quantidade_operacoes=tamanho_base,
        seed=seed + 4
    )

    return CenariosExperimento(
        codigos_busca_existente=codigos_busca_existente,
        codigos_busca_inexistente=codigos_busca_inexistente,
        codigos_remocao=codigos_remocao,
        vendas=vendas,
        operacoes_mistas=operacoes_mistas
    )