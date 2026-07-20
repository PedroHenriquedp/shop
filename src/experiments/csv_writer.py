# src/experiments/csv_writer.py

import csv
from pathlib import Path


COLUNAS_RESULTADO = [
    "estrutura",
    "cenario",
    "tamanho_base",
    "repeticao",
    "quantidade_operacoes",
    "operacoes_sucesso",
    "tempo_total_segundos",
    "tempo_medio_segundos",
    "memoria_pico_bytes",
    "quantidade_elementos",
    "numero_comparacoes",
    "numero_colisoes",
    "fator_carga",
    "maior_lista",
    "numero_rotacoes",
    "altura_arvore",
]


def salvar_resultados(
    resultados: list[dict],
    caminho_arquivo: str | Path = "results/resultados.csv",
    adicionar: bool = False
) -> None:
    """
    Salva os resultados do benchmark em um arquivo CSV.

    Parâmetros:
    - resultados: lista de dicionários produzida pelo benchmark;
    - caminho_arquivo: local em que o CSV será salvo;
    - adicionar:
        False -> sobrescreve o arquivo existente;
        True -> adiciona novas linhas ao arquivo existente.
    """
    caminho = Path(caminho_arquivo)

    # Cria a pasta results, caso ela ainda não exista.
    caminho.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    arquivo_existe = caminho.exists()
    arquivo_tem_conteudo = (
        arquivo_existe
        and caminho.stat().st_size > 0
    )

    modo = "a" if adicionar else "w"

    with caminho.open(
        mode=modo,
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=COLUNAS_RESULTADO,
            extrasaction="ignore"
        )

        # Escreve o cabeçalho quando o arquivo é novo
        # ou quando está sendo sobrescrito.
        if not adicionar or not arquivo_tem_conteudo:
            escritor.writeheader()

        for resultado in resultados:
            linha = {
                coluna: resultado.get(coluna)
                for coluna in COLUNAS_RESULTADO
            }

            escritor.writerow(linha)


def validar_resultados(resultados: list[dict]) -> None:
    """
    Verifica se os resultados possuem os campos mínimos esperados.
    """
    campos_obrigatorios = {
        "estrutura",
        "cenario",
        "tamanho_base",
        "repeticao",
        "quantidade_operacoes",
        "tempo_total_segundos",
        "tempo_medio_segundos",
        "memoria_pico_bytes",
    }

    for indice, resultado in enumerate(
        resultados,
        start=1
    ):
        campos_ausentes = (
            campos_obrigatorios - resultado.keys()
        )

        if campos_ausentes:
            raise ValueError(
                f"Resultado {indice} possui campos ausentes: "
                + ", ".join(sorted(campos_ausentes))
            )


def salvar_resultados_validados(
    resultados: list[dict],
    caminho_arquivo: str | Path = "results/resultados.csv",
    adicionar: bool = False
) -> None:
    """
    Valida e salva os resultados no arquivo CSV.
    """
    validar_resultados(resultados)

    salvar_resultados(
        resultados=resultados,
        caminho_arquivo=caminho_arquivo,
        adicionar=adicionar
    )