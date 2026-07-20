# src/experiments/benchmark.py

from dataclasses import replace
from typing import Callable

from src.experiments.metrics import medir_execucao
from src.experiments.scenarios import (
    CenariosExperimento,
    OperacaoMista,
    OperacaoVenda,
)
from src.inventory.inventory_avl import InventoryAVL
from src.inventory.inventory_hash import InventoryHash
from src.models.produto import Produto


def copiar_produtos(produtos: list[Produto]) -> list[Produto]:
    """
    Cria novas instâncias dos produtos.

    Isso evita que alterações de quantidade ou preço feitas em um
    estoque afetem os experimentos seguintes.
    """
    return [
        replace(produto)
        for produto in produtos
    ]


def criar_estoque(
    estrutura: str,
    tamanho_base: int
) -> InventoryHash | InventoryAVL:
    """
    Cria um estoque vazio usando Hash ou AVL.
    """
    if estrutura == "hash":
        # Mantém o fator de carga inicial abaixo de aproximadamente 0,5.
        tamanho_tabela = max(101, (2 * tamanho_base) + 1)

        return InventoryHash(
            tamanho_tabela=tamanho_tabela
        )

    if estrutura == "avl":
        return InventoryAVL()

    raise ValueError(
        f"Estrutura inválida: {estrutura}. "
        "Use 'hash' ou 'avl'."
    )


def preencher_estoque(
    estoque: InventoryHash | InventoryAVL,
    produtos: list[Produto]
) -> int:
    """
    Cadastra todos os produtos no estoque.

    Retorna a quantidade de produtos efetivamente inseridos.
    """
    inseridos = 0

    for produto in produtos:
        if estoque.cadastrar_produto(produto):
            inseridos += 1

    return inseridos


def executar_buscas(
    estoque: InventoryHash | InventoryAVL,
    codigos: list[str]
) -> int:
    """
    Executa buscas e retorna quantos produtos foram encontrados.
    """
    encontrados = 0

    for codigo in codigos:
        if estoque.buscar_produto(codigo) is not None:
            encontrados += 1

    return encontrados


def executar_remocoes(
    estoque: InventoryHash | InventoryAVL,
    codigos: list[str]
) -> int:
    """
    Executa remoções e retorna quantos produtos foram removidos.
    """
    removidos = 0

    for codigo in codigos:
        if estoque.remover_produto(codigo) is not None:
            removidos += 1

    return removidos


def executar_vendas(
    estoque: InventoryHash | InventoryAVL,
    vendas: list[OperacaoVenda]
) -> int:
    """
    Executa as operações de venda.

    Retorna quantas vendas foram realizadas com sucesso.
    """
    vendas_realizadas = 0

    for venda in vendas:
        resultado = estoque.registrar_venda(
            venda.codigo_barras,
            venda.quantidade
        )

        if resultado:
            vendas_realizadas += 1

    return vendas_realizadas


def obter_valor_operacao(
    operacao: OperacaoMista
) -> int | float | None:
    """
    Permite compatibilidade com duas versões de OperacaoMista:

    - versão com o atributo 'valor';
    - versão anterior com o atributo 'quantidade'.
    """
    if hasattr(operacao, "valor"):
        return operacao.valor

    return operacao.quantidade


def executar_operacoes_mistas(
    estoque: InventoryHash | InventoryAVL,
    operacoes: list[OperacaoMista]
) -> int:
    """
    Executa buscas, vendas, entradas e atualizações de preço.

    Retorna a quantidade de operações concluídas com sucesso.
    """
    sucessos = 0

    for operacao in operacoes:
        valor = obter_valor_operacao(operacao)

        if operacao.tipo == "busca":
            resultado = (
                estoque.buscar_produto(
                    operacao.codigo_barras
                )
                is not None
            )

        elif operacao.tipo == "venda":
            if valor is None:
                resultado = False
            else:
                resultado = estoque.registrar_venda(
                    operacao.codigo_barras,
                    int(valor)
                )

        elif operacao.tipo == "entrada":
            if valor is None:
                resultado = False
            else:
                resultado = estoque.registrar_entrada(
                    operacao.codigo_barras,
                    int(valor)
                )

        elif operacao.tipo == "atualizacao_preco":
            if valor is None:
                resultado = False
            else:
                novo_preco = float(valor)

                # Na primeira versão de scenarios.py, o preço era
                # armazenado em centavos no atributo "quantidade".
                if (
                    not hasattr(operacao, "valor")
                    and isinstance(valor, int)
                ):
                    novo_preco = valor / 100

                resultado = estoque.atualizar_preco(
                    operacao.codigo_barras,
                    novo_preco
                )

        else:
            raise ValueError(
                f"Tipo de operação desconhecido: {operacao.tipo}"
            )

        if resultado:
            sucessos += 1

    return sucessos


def listar_produtos_por_codigo(
    estoque: InventoryHash | InventoryAVL,
    estrutura: str
) -> list[Produto]:
    """
    Gera uma listagem ordenada pelo código de barras.

    Na AVL, o percurso em ordem já devolve os produtos ordenados.
    Na Hash, é necessário recuperar os produtos e usar sorted().
    """
    produtos = estoque.listar_produtos()

    if estrutura == "hash":
        return sorted(
            produtos,
            key=lambda produto: produto.codigo_barras
        )

    return produtos


def montar_resultado(
    estrutura: str,
    cenario: str,
    tamanho_base: int,
    repeticao: int,
    medicao,
    metricas_estrutura: dict,
    operacoes_sucesso: int | None = None
) -> dict:
    """
    Padroniza as linhas de resultado da Hash e da AVL.
    """
    return {
        "estrutura": estrutura,
        "cenario": cenario,
        "tamanho_base": tamanho_base,
        "repeticao": repeticao,
        "quantidade_operacoes":
            medicao.quantidade_operacoes,
        "operacoes_sucesso": operacoes_sucesso,
        "tempo_total_segundos":
            medicao.tempo_total,
        "tempo_medio_segundos":
            medicao.tempo_medio,
        "memoria_pico_bytes":
            medicao.memoria_pico_bytes,
        "quantidade_elementos":
            metricas_estrutura.get(
                "quantidade_elementos"
            ),
        "numero_comparacoes":
            metricas_estrutura.get(
                "numero_comparacoes"
            ),
        "numero_colisoes":
            metricas_estrutura.get(
                "numero_colisoes"
            ),
        "fator_carga":
            metricas_estrutura.get(
                "fator_carga"
            ),
        "maior_lista":
            metricas_estrutura.get(
                "maior_lista"
            ),
        "numero_rotacoes":
            metricas_estrutura.get(
                "numero_rotacoes"
            ),
        "altura_arvore":
            metricas_estrutura.get(
                "altura_arvore"
            ),
    }


def medir_cenario_com_estoque_preenchido(
    estrutura: str,
    produtos: list[Produto],
    cenario: str,
    funcao: Callable,
    quantidade_operacoes: int,
    repeticao: int,
    *args
) -> dict:
    """
    Cria e preenche um estoque antes de medir um cenário.

    O tempo da inserção inicial não é incluído na medição.
    """
    estoque = criar_estoque(
        estrutura,
        len(produtos)
    )

    preencher_estoque(
        estoque,
        copiar_produtos(produtos)
    )

    # Desconsidera comparações, colisões e rotações da montagem
    # inicial do estoque.
    estoque.reiniciar_metricas()

    medicao = medir_execucao(
        funcao,
        quantidade_operacoes,
        estoque,
        *args
    )

    metricas = estoque.obter_metricas()

    return montar_resultado(
        estrutura=estrutura,
        cenario=cenario,
        tamanho_base=len(produtos),
        repeticao=repeticao,
        medicao=medicao,
        metricas_estrutura=metricas,
        operacoes_sucesso=medicao.resultado
    )


def executar_benchmark_estrutura(
    estrutura: str,
    produtos: list[Produto],
    cenarios: CenariosExperimento,
    repeticao: int = 1
) -> list[dict]:
    """
    Executa todos os cenários para uma estrutura.

    Retorna uma lista de dicionários, um para cada cenário.
    """
    resultados: list[dict] = []
    tamanho_base = len(produtos)

    # 1. Inserção
    estoque_insercao = criar_estoque(
        estrutura,
        tamanho_base
    )

    produtos_insercao = copiar_produtos(produtos)

    medicao_insercao = medir_execucao(
        preencher_estoque,
        tamanho_base,
        estoque_insercao,
        produtos_insercao
    )

    resultados.append(
        montar_resultado(
            estrutura=estrutura,
            cenario="insercao",
            tamanho_base=tamanho_base,
            repeticao=repeticao,
            medicao=medicao_insercao,
            metricas_estrutura=(
                estoque_insercao.obter_metricas()
            ),
            operacoes_sucesso=medicao_insercao.resultado
        )
    )

    # 2. Busca bem-sucedida
    resultados.append(
        medir_cenario_com_estoque_preenchido(
            estrutura,
            produtos,
            "busca_existente",
            executar_buscas,
            len(cenarios.codigos_busca_existente),
            repeticao,
            cenarios.codigos_busca_existente
        )
    )

    # 3. Busca malsucedida
    resultados.append(
        medir_cenario_com_estoque_preenchido(
            estrutura,
            produtos,
            "busca_inexistente",
            executar_buscas,
            len(cenarios.codigos_busca_inexistente),
            repeticao,
            cenarios.codigos_busca_inexistente
        )
    )

    # 4. Remoção
    resultados.append(
        medir_cenario_com_estoque_preenchido(
            estrutura,
            produtos,
            "remocao",
            executar_remocoes,
            len(cenarios.codigos_remocao),
            repeticao,
            cenarios.codigos_remocao
        )
    )

    # 5. Vendas
    resultados.append(
        medir_cenario_com_estoque_preenchido(
            estrutura,
            produtos,
            "vendas",
            executar_vendas,
            len(cenarios.vendas),
            repeticao,
            cenarios.vendas
        )
    )

    # 6. Operações mistas
    resultados.append(
        medir_cenario_com_estoque_preenchido(
            estrutura,
            produtos,
            "operacoes_mistas",
            executar_operacoes_mistas,
            len(cenarios.operacoes_mistas),
            repeticao,
            cenarios.operacoes_mistas
        )
    )

    # 7. Listagem ordenada pelo código de barras
    estoque_listagem = criar_estoque(
        estrutura,
        tamanho_base
    )

    preencher_estoque(
        estoque_listagem,
        copiar_produtos(produtos)
    )

    estoque_listagem.reiniciar_metricas()

    medicao_listagem = medir_execucao(
        listar_produtos_por_codigo,
        tamanho_base,
        estoque_listagem,
        estrutura
    )

    resultados.append(
        montar_resultado(
            estrutura=estrutura,
            cenario="listagem_codigo",
            tamanho_base=tamanho_base,
            repeticao=repeticao,
            medicao=medicao_listagem,
            metricas_estrutura=(
                estoque_listagem.obter_metricas()
            ),
            operacoes_sucesso=len(
                medicao_listagem.resultado
            )
        )
    )

    return resultados


def executar_benchmark(
    produtos: list[Produto],
    cenarios: CenariosExperimento,
    repeticao: int = 1
) -> list[dict]:
    """
    Executa os mesmos cenários na Hash e na AVL.
    """
    resultados: list[dict] = []

    resultados.extend(
        executar_benchmark_estrutura(
            estrutura="hash",
            produtos=produtos,
            cenarios=cenarios,
            repeticao=repeticao
        )
    )

    resultados.extend(
        executar_benchmark_estrutura(
            estrutura="avl",
            produtos=produtos,
            cenarios=cenarios,
            repeticao=repeticao
        )
    )

    return resultados