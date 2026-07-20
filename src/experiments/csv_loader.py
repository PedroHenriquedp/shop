# src/experiments/csv_loader.py

import csv
from datetime import date
from pathlib import Path
from datetime import datetime

from src.models.produto import Produto


def carregar_produtos(caminho_arquivo: str | Path) -> list[Produto]:
    """
    Lê um arquivo CSV e transforma cada linha em um Produto.

    O CSV deve conter as colunas:
    codigo_barras, nome, categoria, preco, quantidade e validade.
    """
    caminho = Path(caminho_arquivo)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    produtos: list[Produto] = []

    with caminho.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:
        leitor = csv.DictReader(arquivo)

        colunas_obrigatorias = {
            "codigo_barras",
            "nome",
            "categoria",
            "preco",
            "quantidade",
            "validade"
        }

        if leitor.fieldnames is None:
            raise ValueError(
                "O arquivo CSV não possui cabeçalho."
            )

        colunas_encontradas = set(leitor.fieldnames)

        colunas_ausentes = (
            colunas_obrigatorias - colunas_encontradas
        )

        if colunas_ausentes:
            raise ValueError(
                "Colunas ausentes no CSV: "
                + ", ".join(sorted(colunas_ausentes))
            )

        for numero_linha, linha in enumerate(
            leitor,
            start=2
        ):
            try:
                validade_texto = linha["validade"].strip()

                validade = (
                    datetime.strptime(
                        validade_texto,
                        "%d/%m/%Y"
                    ).date()
                        if validade_texto
                        else None
                )

                produto = Produto(
                    codigo_barras=linha[
                        "codigo_barras"
                    ].strip(),
                    nome=linha["nome"].strip(),
                    categoria=linha["categoria"].strip(),
                    preco=float(
                        linha["preco"].replace(",", ".")
                    ),
                    quantidade=int(linha["quantidade"]),
                    validade=validade
                )

                produtos.append(produto)

            except (ValueError, TypeError, KeyError) as erro:
                raise ValueError(
                    f"Erro na linha {numero_linha}: {erro}"
                ) from erro

    return produtos