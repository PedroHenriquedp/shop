from __future__ import annotations

import csv
import json
import os
import random
from collections import defaultdict
from datetime import date, timedelta
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from statistics import mean, stdev
from urllib.parse import parse_qs, urlparse

from src.experiments.benchmark import executar_benchmark
from src.experiments.csv_loader import carregar_produtos
from src.experiments.scenarios import criar_cenarios
from src.models.produto import Produto


PASTA_PROJETO = Path(__file__).resolve().parents[2]
ARQUIVO_RESULTADOS = PASTA_PROJETO / "results" / "resultados.csv"
MAX_PRODUTOS_TESTE_AO_VIVO = 100_000
BASES_OFICIAIS = {100, 1000, 10000}


def criar_produtos_teste_ao_vivo(quantidade: int) -> list[Produto]:
    """Gera uma base temporária determinística para a exploração no frontend."""
    gerador = random.Random(42)
    categorias = {
        "Eletrônicos": ["Notebook", "Smartphone", "Fone Bluetooth"],
        "Casa e cozinha": ["Cafeteira", "Air Fryer", "Liquidificador"],
        "Mercado": ["Café especial", "Chocolate premium", "Azeite"],
    }
    marcas = ["Aurora", "Nexora", "PrimeBox", "PixelPro"]
    produtos = []

    for indice in range(quantidade):
        categoria = gerador.choice(list(categorias))
        produtos.append(
            Produto(
                codigo_barras=str(789_000_000_0000 + indice),
                nome=f"{gerador.choice(categorias[categoria])} {gerador.choice(marcas)} {indice + 1}",
                categoria=categoria,
                preco=round(gerador.uniform(9.9, 5_999.9), 2),
                quantidade=gerador.randint(1, 250),
                validade=date.today() + timedelta(days=gerador.randint(30, 1825)),
            )
        )

    return produtos


def media_e_desvio(valores: list[float]) -> tuple[float, float]:
    return mean(valores), stdev(valores) if len(valores) > 1 else 0.0


def carregar_resultados_consolidados(caminho: Path = ARQUIVO_RESULTADOS) -> dict:
    """Agrupa as 30 repetições sem alterar os dados brutos do artigo."""
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de resultados não encontrado: {caminho}")

    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))

    grupos: dict[tuple[str, str, int], list[dict[str, str]]] = defaultdict(list)
    for linha in linhas:
        grupos[(linha["estrutura"], linha["cenario"], int(linha["tamanho_base"]))].append(linha)

    resultados = []
    for (estrutura, cenario, tamanho_base), amostras in sorted(grupos.items(), key=lambda item: (item[0][2], item[0][1], item[0][0])):
        def estatistica(campo: str) -> tuple[float | None, float | None]:
            valores = [float(linha[campo]) for linha in amostras if linha.get(campo, "").strip()]
            return media_e_desvio(valores) if valores else (None, None)

        tempo_medio, tempo_desvio = estatistica("tempo_total_segundos")
        memoria_media, _ = estatistica("memoria_pico_bytes")
        comparacoes_media, _ = estatistica("numero_comparacoes")
        colisoes_media, _ = estatistica("numero_colisoes")
        fator_carga_medio, _ = estatistica("fator_carga")
        maior_lista_media, _ = estatistica("maior_lista")
        rotacoes_media, _ = estatistica("numero_rotacoes")
        altura_media, _ = estatistica("altura_arvore")
        sucessos_media, _ = estatistica("operacoes_sucesso")

        resultados.append({
            "estrutura": estrutura,
            "cenario": cenario,
            "tamanho_base": tamanho_base,
            "amostras": len(amostras),
            "quantidade_operacoes": int(amostras[0]["quantidade_operacoes"]),
            "operacoes_sucesso_media": sucessos_media,
            "tempo_medio_segundos": tempo_medio,
            "tempo_desvio_segundos": tempo_desvio,
            "memoria_pico_media_bytes": memoria_media,
            "comparacoes_media": comparacoes_media,
            "colisoes_media": colisoes_media,
            "fator_carga_medio": fator_carga_medio,
            "maior_lista_media": maior_lista_media,
            "rotacoes_media": rotacoes_media,
            "altura_media": altura_media,
        })

    cenarios = ["insercao", "busca_existente", "busca_inexistente", "remocao", "vendas", "operacoes_mistas", "listagem_codigo"]
    return {
        "metodologia": {
            "fonte": "results/resultados.csv",
            "bases": sorted({resultado["tamanho_base"] for resultado in resultados}),
            "cenarios": cenarios,
            "repeticoes": max(int(linha["repeticao"]) for linha in linhas),
            "linhas_brutas": len(linhas),
        },
        "resultados": resultados,
    }


class AppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(PASTA_PROJETO), **kwargs)

    def do_GET(self) -> None:
        rota = urlparse(self.path)
        if rota.path == "/api/resultados":
            self.responder_resultados()
            return
        if rota.path == "/api/teste-ao-vivo":
            self.responder_teste_ao_vivo(rota.query)
            return
        if rota.path == "/":
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "/frontend/")
            self.end_headers()
            return
        super().do_GET()

    def end_headers(self) -> None:
        if self.path.startswith("/frontend/"):
            self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def responder_resultados(self) -> None:
        try:
            self.enviar_json(carregar_resultados_consolidados())
        except FileNotFoundError as erro:
            self.enviar_json({"erro": str(erro)}, status=HTTPStatus.NOT_FOUND)

    def responder_teste_ao_vivo(self, query: str) -> None:
        parametros = parse_qs(query)
        try:
            tamanho_base = int(parametros.get("quantidade", [""])[0])
        except ValueError:
            tamanho_base = 0

        if tamanho_base < 1 or tamanho_base > MAX_PRODUTOS_TESTE_AO_VIVO:
            self.enviar_json(
                {"erro": "Informe uma quantidade entre 1 e 100.000 produtos."},
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        if tamanho_base in BASES_OFICIAIS:
            caminho_base = PASTA_PROJETO / "data" / f"produtos_{tamanho_base}.csv"
            produtos = carregar_produtos(caminho_base)
            origem = "base oficial em CSV"
        else:
            produtos = criar_produtos_teste_ao_vivo(tamanho_base)
            origem = "base temporária gerada em memória"
        resultados = executar_benchmark(
            produtos=produtos,
            cenarios=criar_cenarios(produtos),
            repeticao=1,
        )
        self.enviar_json(
            {
                "tipo": "execucao_pontual",
                "tamanho_base": tamanho_base,
                "origem": origem,
                "resultados": resultados,
            }
        )

    def enviar_json(self, dados: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    porta = int(os.getenv("PORT", "8000"))
    servidor = ThreadingHTTPServer((host, porta), AppHandler)
    print(f"Visualização: http://localhost:{porta}/frontend/")
    print(f"Resultados: http://localhost:{porta}/api/resultados")
    servidor.serve_forever()


if __name__ == "__main__":
    main()
