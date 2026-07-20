# src/main.py

from pathlib import Path
from time import perf_counter

from src.experiments.benchmark import executar_benchmark
from src.experiments.csv_loader import carregar_produtos
from src.experiments.csv_writer import salvar_resultados_validados
from src.experiments.scenarios import criar_cenarios


# Pasta raiz do projeto.
PASTA_PROJETO = Path(__file__).resolve().parent.parent

PASTA_DADOS = PASTA_PROJETO / "data"
PASTA_RESULTADOS = PASTA_PROJETO / "results"

ARQUIVO_RESULTADOS = PASTA_RESULTADOS / "resultados.csv"

ARQUIVOS_ENTRADA = [
    PASTA_DADOS / "produtos_100.csv",
    PASTA_DADOS / "produtos_1000.csv",
    PASTA_DADOS / "produtos_10000.csv",
]

# Começaremos com cinco repetições para validar o experimento.
QUANTIDADE_REPETICOES = 30

# Mantém os cenários reproduzíveis.
SEED = 42


def executar_experimentos() -> list[dict]:
    """
    Executa o benchmark para todas as bases e repetições.

    Retorna uma lista contendo todos os resultados.
    """
    todos_resultados: list[dict] = []

    quantidade_bases = len(ARQUIVOS_ENTRADA)
    total_execucoes = quantidade_bases * QUANTIDADE_REPETICOES
    execucao_atual = 0

    inicio_geral = perf_counter()

    print("=" * 60)
    print("INÍCIO DOS EXPERIMENTOS")
    print("=" * 60)

    for caminho_arquivo in ARQUIVOS_ENTRADA:
        print(f"\nCarregando arquivo: {caminho_arquivo.name}")

        produtos = carregar_produtos(caminho_arquivo)

        tamanho_base = len(produtos)

        print(f"Produtos carregados: {tamanho_base}")

        # Os cenários são criados uma única vez para cada base.
        # Assim, todas as repetições e estruturas recebem
        # exatamente as mesmas operações.
        cenarios = criar_cenarios(
            produtos=produtos,
            seed=SEED
        )

        for repeticao in range(
            1,
            QUANTIDADE_REPETICOES + 1
        ):
            execucao_atual += 1

            print(
                f"\n[{execucao_atual}/{total_execucoes}] "
                f"Base: {tamanho_base} produtos | "
                f"Repetição: {repeticao}/{QUANTIDADE_REPETICOES}"
            )

            inicio_execucao = perf_counter()

            resultados = executar_benchmark(
                produtos=produtos,
                cenarios=cenarios,
                repeticao=repeticao
            )

            todos_resultados.extend(resultados)

            tempo_execucao = perf_counter() - inicio_execucao

            print(
                f"Concluída em {tempo_execucao:.4f} segundos."
            )

    tempo_total = perf_counter() - inicio_geral

    print("\n" + "=" * 60)
    print("EXPERIMENTOS CONCLUÍDOS")
    print(f"Tempo total: {tempo_total:.2f} segundos")
    print(f"Resultados gerados: {len(todos_resultados)}")
    print("=" * 60)

    return todos_resultados


def main() -> None:
    """
    Executa os experimentos e salva os resultados em CSV.
    """
    try:
        resultados = executar_experimentos()

        salvar_resultados_validados(
            resultados=resultados,
            caminho_arquivo=ARQUIVO_RESULTADOS,
            adicionar=False
        )

        print(
            f"\nResultados salvos em:\n{ARQUIVO_RESULTADOS}"
        )

    except FileNotFoundError as erro:
        print("\nErro ao localizar um arquivo:")
        print(erro)

    except ValueError as erro:
        print("\nErro nos dados ou na configuração:")
        print(erro)

    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")

    except Exception as erro:
        print("\nOcorreu um erro inesperado:")
        print(f"{type(erro).__name__}: {erro}")
        raise


if __name__ == "__main__":
    main()