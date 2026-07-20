# src/experiments/analise_resultados.py

from __future__ import annotations

import csv
import math
import platform
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import mean, stdev
from typing import Callable


PASTA_PROJETO = Path(__file__).resolve().parent.parent.parent
ARQUIVO_CSV = PASTA_PROJETO / "results" / "resultados.csv"
ARQUIVO_TEX = PASTA_PROJETO / "results" / "resultados_experimentos.tex"

CENARIOS_ORDEM = [
    "insercao",
    "busca_existente",
    "busca_inexistente",
    "remocao",
    "vendas",
    "operacoes_mistas",
    "listagem_codigo",
]

ROTULOS_CENARIO = {
    "insercao": "Inserção",
    "busca_existente": "Busca existente",
    "busca_inexistente": "Busca inexistente",
    "remocao": "Remoção",
    "vendas": "Vendas",
    "operacoes_mistas": "Operações mistas",
    "listagem_codigo": "Listagem ordenada",
}

DOMINIO_CENARIO = {
    "insercao": "Cadastro / importação de estoque",
    "busca_existente": "PDV: leitura de código de barras",
    "busca_inexistente": "PDV: código não cadastrado",
    "remocao": "Baixa de produtos (10\\% da base)",
    "vendas": "Saída de estoque no caixa",
    "operacoes_mistas": "Fluxo combinado do dia (busca, venda, entrada, preço)",
    "listagem_codigo": "Backoffice: relatório ordenado",
}


@dataclass
class Estatistica:
    media: float
    desvio: float
    amostras: int

    @classmethod
    def vazia(cls) -> Estatistica:
        return cls(media=0.0, desvio=0.0, amostras=0)

    @classmethod
    def calcular(cls, valores: list[float]) -> Estatistica:
        if not valores:
            return cls.vazia()

        media_valor = mean(valores)
        desvio_valor = stdev(valores) if len(valores) > 1 else 0.0

        return cls(
            media=media_valor,
            desvio=desvio_valor,
            amostras=len(valores),
        )


def carregar_csv(caminho: Path) -> list[dict[str, str]]:
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    with caminho.open(newline="", encoding="utf-8-sig") as arquivo:
        return list(csv.DictReader(arquivo))


def parse_float(valor: str | None) -> float | None:
    if valor is None or valor.strip() == "":
        return None

    return float(valor)


def agrupar_por_chave(
    linhas: list[dict[str, str]],
    campo: str,
) -> dict[tuple[str, str, int], list[float]]:
    grupos: dict[tuple[str, str, int], list[float]] = defaultdict(list)

    for linha in linhas:
        valor = parse_float(linha.get(campo))
        if valor is None:
            continue

        chave = (
            linha["estrutura"],
            linha["cenario"],
            int(linha["tamanho_base"]),
        )
        grupos[chave].append(valor)

    return grupos


def formatar_numero(
    valor: float,
    casas: int = 6,
) -> str:
    texto = f"{valor:.{casas}f}".replace(".", "{,}")
    return texto


def normalizar_cientifico(valor: float) -> tuple[float, int]:
    if valor == 0.0:
        return 0.0, 0

    exponente = math.floor(math.log10(abs(valor)))
    mantissa = valor / (10 ** exponente)

    if abs(mantissa) >= 10:
        mantissa /= 10
        exponente += 1

    return mantissa, exponente


def formatar_sufixo_expoente(exponente: int) -> str:
    if exponente == 0:
        return ""

    return f"\\,\\mathrm{{e}}^{{{exponente}}}"


def formatar_valor_cientifico(
    valor: float,
    casas: int = 2,
) -> str:
    mantissa, exponente = normalizar_cientifico(valor)

    if exponente == 0:
        return f"${formatar_numero(mantissa, casas)}$"

    return (
        f"${formatar_numero(mantissa, casas)}"
        f"{formatar_sufixo_expoente(exponente)}$"
    )


def formatar_media_desvio(
    estatistica: Estatistica,
    casas: int = 2,
) -> str:
    if estatistica.amostras == 0:
        return "---"

    if estatistica.media == 0.0 and estatistica.desvio == 0.0:
        return "$0$"

    referencia = (
        estatistica.media
        if estatistica.media != 0.0
        else estatistica.desvio
    )
    _, exponente = normalizar_cientifico(referencia)
    escala = 10 ** exponente

    media = estatistica.media / escala
    desvio = estatistica.desvio / escala

    if exponente == 0:
        return (
            f"${formatar_numero(media, casas)} \\pm "
            f"{formatar_numero(desvio, casas)}$"
        )

    return (
        f"${formatar_numero(media, casas)} \\pm "
        f"{formatar_numero(desvio, casas)}"
        f"{formatar_sufixo_expoente(exponente)}$"
    )


def formatar_bytes(valor: float) -> str:
    if valor >= 1024 * 1024:
        return f"${formatar_numero(valor / (1024 * 1024), 2)}\\,$ MiB"

    if valor >= 1024:
        return f"${formatar_numero(valor / 1024, 1)}\\,$ KiB"

    return f"${formatar_numero(valor, 0)}\\,$ B"


def obter_estatistica(
    grupos: dict[tuple[str, str, int], list[float]],
    estrutura: str,
    cenario: str,
    tamanho: int,
) -> Estatistica:
    return Estatistica.calcular(
        grupos.get((estrutura, cenario, tamanho), [])
    )


def calcular_speedup(
    tempos_hash: Estatistica,
    tempos_avl: Estatistica,
) -> str:
    if (
        tempos_hash.amostras == 0
        or tempos_avl.amostras == 0
        or tempos_hash.media <= 0
    ):
        return "---"

    razao = tempos_avl.media / tempos_hash.media
    return f"${formatar_numero(razao, 2)}\\times$"


def vencedor(
    tempos_hash: Estatistica,
    tempos_avl: Estatistica,
) -> str:
    if tempos_hash.amostras == 0 or tempos_avl.amostras == 0:
        return "---"

    if tempos_hash.media < tempos_avl.media:
        return "Hash"

    if tempos_avl.media < tempos_hash.media:
        return "AVL"

    return "Empate"


def descobrir_tamanhos(linhas: list[dict[str, str]]) -> list[int]:
    return sorted(
        {
            int(linha["tamanho_base"])
            for linha in linhas
        }
    )


def descobrir_repeticoes(linhas: list[dict[str, str]]) -> int:
    repeticoes = {
        int(linha["repeticao"])
        for linha in linhas
    }
    return max(repeticoes) if repeticoes else 0


def gerar_tabela_transposta(
    linhas: list[dict[str, str]],
    tamanhos: list[int],
    campo: str,
    formatar_valor: Callable[[Estatistica], str],
    caption: str,
    label: str,
    fonte_pequena: bool = False,
) -> str:
    """
    Layout transposto: linhas = cenário × estrutura, colunas = tamanhos da base.
    """
    grupos = agrupar_por_chave(linhas, campo)
    colunas = "ll" + "c" * len(tamanhos)
    cabecalho = " & ".join(
        f"$n={tamanho}$"
        for tamanho in tamanhos
    )

    corpo: list[str] = []

    for cenario in CENARIOS_ORDEM:
        for indice, estrutura in enumerate(("hash", "avl")):
            rotulo_cenario = ROTULOS_CENARIO[cenario] if indice == 0 else ""
            rotulo_estrutura = "Hash" if estrutura == "hash" else "AVL"
            celulas = [
                rotulo_cenario,
                rotulo_estrutura,
            ]

            for tamanho in tamanhos:
                stats = obter_estatistica(
                    grupos,
                    estrutura,
                    cenario,
                    tamanho,
                )
                celulas.append(formatar_valor(stats))

            corpo.append(" & ".join(celulas) + r" \\")

    inicio_tabela = r"  \begin{tabular}{" + colunas + "}"
    fim_tabela = r"  \end{tabular}"

    if fonte_pequena:
        inicio_tabela = r"  \footnotesize" + "\n" + inicio_tabela
        fim_tabela = fim_tabela + "\n" + r"  \normalsize"

    return "\n".join(
        [
            r"\begin{table}[H]",
            r"  \centering",
            f"  \\caption{{{caption}}}",
            f"  \\label{{{label}}}",
            inicio_tabela,
            r"    \hline",
            f"    Cenário & Estr. & {cabecalho} \\\\",
            r"    \hline",
            *[f"    {linha}" for linha in corpo],
            r"    \hline",
            fim_tabela,
            r"\end{table}",
        ]
    )


def gerar_tabela_tempos(
    linhas: list[dict[str, str]],
    tamanhos: list[int],
) -> str:
    return gerar_tabela_transposta(
        linhas=linhas,
        tamanhos=tamanhos,
        campo="tempo_total_segundos",
        formatar_valor=formatar_media_desvio,
        caption=(
            "Tempo total médio ($\\pm$ desvio padrão, em segundos; "
            "formato $a \\pm b\\,\\mathrm{e}^{k}$). "
            "Linhas agrupadas por cenário; colunas indicam o tamanho da base."
        ),
        label="tab:tempos-total",
        fonte_pequena=True,
    )


def gerar_tabela_speedup(
    linhas: list[dict[str, str]],
    tamanhos: list[int],
) -> str:
    grupos = agrupar_por_chave(linhas, "tempo_total_segundos")
    colunas = "l" + "c" * len(tamanhos)

    corpo: list[str] = []

    for cenario in CENARIOS_ORDEM:
        celulas = [ROTULOS_CENARIO[cenario]]

        for tamanho in tamanhos:
            hash_stats = obter_estatistica(grupos, "hash", cenario, tamanho)
            avl_stats = obter_estatistica(grupos, "avl", cenario, tamanho)
            celulas.append(calcular_speedup(hash_stats, avl_stats))

        corpo.append(" & ".join(celulas) + r" \\")

    cabecalho = " & ".join(
        f"$n={tamanho}$"
        for tamanho in tamanhos
    )

    return "\n".join(
        [
            r"\begin{table}[H]",
            r"  \centering",
            r"  \caption{Razão AVL/Hash no tempo total médio. Valores acima de $1{,}0\times$ indicam vantagem da Hash.}",
            r"  \label{tab:speedup}",
            f"  \\begin{{tabular}}{{{colunas}}}",
            r"    \hline",
            f"    Cenário & {cabecalho} \\\\",
            r"    \hline",
            *[f"    {linha}" for linha in corpo],
            r"    \hline",
            r"  \end{tabular}",
            r"\end{table}",
        ]
    )


def gerar_tabela_memoria(
    linhas: list[dict[str, str]],
    tamanhos: list[int],
) -> str:
    def formatar_memoria(stats: Estatistica) -> str:
        return formatar_bytes(stats.media)

    return gerar_tabela_transposta(
        linhas=linhas,
        tamanhos=tamanhos,
        campo="memoria_pico_bytes",
        formatar_valor=formatar_memoria,
        caption=(
            "Memória pico média medida com \\texttt{tracemalloc} durante cada cenário."
        ),
        label="tab:memoria",
    )


def gerar_tabela_metricas_estruturais(
    linhas: list[dict[str, str]],
    tamanhos: list[int],
) -> str:
    campos = [
        ("numero_colisoes", "Colisões (Hash)", "hash"),
        ("fator_carga", "Fator de carga (Hash)", "hash"),
        ("maior_lista", "Maior lista de colisão (Hash)", "hash"),
        ("numero_rotacoes", "Rotações (AVL)", "avl"),
        ("altura_arvore", "Altura da árvore (AVL)", "avl"),
    ]

    blocos: list[str] = []

    for campo, rotulo, estrutura in campos:
        grupos = agrupar_por_chave(linhas, campo)
        colunas = "l" + "c" * len(tamanhos)
        cabecalho = " & ".join(
            f"$n={tamanho}$"
            for tamanho in tamanhos
        )

        if estrutura == "hash" and campo == "fator_carga":
            celulas = [
                formatar_numero(
                    obter_estatistica(
                        grupos,
                        estrutura,
                        "insercao",
                        tamanho,
                    ).media,
                    3,
                )
                for tamanho in tamanhos
            ]
        else:
            celulas = [
                formatar_numero(
                    obter_estatistica(
                        grupos,
                        estrutura,
                        "insercao",
                        tamanho,
                    ).media,
                    0 if campo in {"numero_colisoes", "maior_lista", "numero_rotacoes", "altura_arvore"} else 3,
                )
                for tamanho in tamanhos
            ]

        blocos.extend(
            [
                r"\begin{table}[H]",
                r"  \centering",
                f"  \\caption{{Média de {rotulo} após inserção completa da base.}}",
                f"  \\label{{tab:{campo.replace('_', '-')}-insercao}}",
                f"  \\begin{{tabular}}{{{colunas}}}",
                r"    \hline",
                f"    {rotulo} & {cabecalho} \\\\",
                r"    \hline",
                f"    Média & {' & '.join(f'${valor}$' for valor in celulas)} \\\\",
                r"    \hline",
                r"  \end{tabular}",
                r"\end{table}",
            ]
        )

    return "\n".join(blocos)


def gerar_tabela_cenarios() -> str:
    linhas = [
        f"    {ROTULOS_CENARIO[cenario]} & {DOMINIO_CENARIO[cenario]} \\\\"
        for cenario in CENARIOS_ORDEM
    ]

    return "\n".join(
        [
            r"\begin{table}[H]",
            r"  \centering",
            r"  \caption{Cenários experimentais e correspondência com o domínio da aplicação.}",
            r"  \label{tab:cenarios}",
            r"  \begin{tabular}{ll}",
            r"    \hline",
            r"    Cenário & Simulação no sistema de estoque \\",
            r"    \hline",
            *linhas,
            r"    \hline",
            r"  \end{tabular}",
            r"\end{table}",
        ]
    )


def formatar_tempo_simples(estatistica: Estatistica, casas: int = 2) -> str:
    if estatistica.amostras == 0:
        return "---"

    return formatar_valor_cientifico(estatistica.media, casas)


def gerar_discussao_narrativa(
    linhas: list[dict[str, str]],
    tamanhos: list[int],
) -> list[str]:
    """
    Reproduz a narrativa original da seção de resultados, com valores
    alinhados às médias consolidadas em results/resultados.csv.
    """
    grupos_tempo = agrupar_por_chave(linhas, "tempo_total_segundos")
    grupos_rotacoes = agrupar_por_chave(linhas, "numero_rotacoes")
    grupos_altura = agrupar_por_chave(linhas, "altura_arvore")

    base_referencia = 1000 if 1000 in tamanhos else max(tamanhos)
    base_pequena = 100 if 100 in tamanhos else min(tamanhos)

    insercao_hash = obter_estatistica(
        grupos_tempo, "hash", "insercao", base_referencia
    )
    insercao_avl = obter_estatistica(
        grupos_tempo, "avl", "insercao", base_referencia
    )
    busca_hash = obter_estatistica(
        grupos_tempo, "hash", "busca_existente", base_pequena
    )
    busca_avl = obter_estatistica(
        grupos_tempo, "avl", "busca_existente", base_pequena
    )
    lista_hash_ref = obter_estatistica(
        grupos_tempo, "hash", "listagem_codigo", base_referencia
    )
    lista_avl_ref = obter_estatistica(
        grupos_tempo, "avl", "listagem_codigo", base_referencia
    )
    lista_hash_grande = obter_estatistica(
        grupos_tempo, "hash", "listagem_codigo", max(tamanhos)
    )
    lista_avl_grande = obter_estatistica(
        grupos_tempo, "avl", "listagem_codigo", max(tamanhos)
    )

    rotacoes_avl = obter_estatistica(
        grupos_rotacoes, "avl", "insercao", base_referencia
    )
    altura_avl = obter_estatistica(
        grupos_altura, "avl", "insercao", base_referencia
    )

    altura_inteira = int(round(altura_avl.media))

    return [
        (
            "A análise dos resultados de inserção revela uma disparidade "
            "significativa: a Tabela Hash completou a operação em "
            f"{formatar_tempo_simples(insercao_hash)} segundos, enquanto a "
            "Árvore AVL demandou "
            f"{formatar_tempo_simples(insercao_avl)} segundos "
            f"(Tabela~\\ref{{tab:tempos-total}}, $n={base_referencia}$). "
            "Esse comportamento prático justifica-se teoricamente pelo esforço "
            "computacional exigido para o balanceamento da árvore. Durante a "
            f"inserção dos {base_referencia} registros, a Árvore AVL executou "
            "em média "
            f"{formatar_numero(rotacoes_avl.media, 0)} rotações estruturais "
            r"(Tabela~\ref{tab:numero-rotacoes-insercao}) para estabilizar "
            "seus nós em uma altura final igual a "
            f"{altura_inteira} níveis "
            r"(Tabela~\ref{tab:altura-arvore-insercao}), gerando uma "
            "sobrecarga de processamento ausente na Tabela Hash."
        ),
        "",
        (
            "No cenário de simulação de Frente de Caixa (representado pelas "
            "operações de busca única), a Tabela Hash confirmou sua "
            "superioridade de tempo constante, localizando os elementos de "
            f"forma mais ágil ({formatar_tempo_simples(busca_hash)} para "
            f"100 buscas) que a árvore balanceada "
            f"({formatar_tempo_simples(busca_avl)}; "
            f"Tabela~\\ref{{tab:tempos-total}}, $n={base_pequena}$). Esse ganho "
            "ocorre porque a Hash acessa o endereço físico de memória "
            "diretamente via índice calculado, ao passo que a AVL obriga o "
            "algoritmo de busca a navegar de forma descendente pelos seus "
            "ponteiros estruturais, realizando até "
            f"{altura_inteira} comparações lógicas por item buscado no pior "
            r"caso (Tabela~\ref{tab:altura-arvore-insercao}, "
            f"$n={base_referencia}$)."
        ),
        "",
        (
            "Na operação de listagem ordenada, crucial para os relatórios "
            "administrativos de backoffice, a AVL apresentou tempo total "
            "médio inferior ao da Hash quando a base cresce "
            f"({formatar_tempo_simples(lista_avl_ref)} frente a "
            f"{formatar_tempo_simples(lista_hash_ref)} em $n={base_referencia}$; "
            f"{formatar_tempo_simples(lista_avl_grande)} frente a "
            f"{formatar_tempo_simples(lista_hash_grande)} em "
            f"$n={max(tamanhos)}$). Sob uma análise de escalabilidade, "
            "ressalta-se que a ausência de ordem nativa na Hash obriga o "
            "sistema a exportar os dados para um vetor auxiliar e aplicar "
            "rotinas de ordenação externa de custo $O(n \\log n)$, enquanto "
            "a AVL preserva a complexidade estrita de $O(n)$ pelo percurso "
            "de seus nós, conforme a Tabela~\\ref{tab:tempos-total}."
        ),
        "",
        (
            r"A Tabela~\ref{tab:speedup} sintetiza a razão AVL/Hash em todos "
            r"os cenários: valores superiores a $1{,}0\times$ indicam "
            r"vantagem da Hash nas operações pontuais de caixa, enquanto a "
            r"\emph{listagem ordenada} confirma o cenário inverso. A "
            r"Tabela~\ref{tab:memoria} evidencia o menor consumo de memória "
            r"pico da Hash nas inserções, enquanto as métricas de colisões "
            r"e encadeamento (\ref{tab:numero-colisoes-insercao}, "
            r"\ref{tab:fator-carga-insercao} e \ref{tab:maior-lista-insercao}) "
            r"explicam o comportamento observado na Tabela Hash."
        ),
    ]


def gerar_paragrafo_destaque(
    linhas: list[dict[str, str]],
    tamanhos: list[int],
) -> str:
    grupos = agrupar_por_chave(linhas, "tempo_total_segundos")
    maior = max(tamanhos)

    insercao_hash = obter_estatistica(grupos, "hash", "insercao", maior)
    insercao_avl = obter_estatistica(grupos, "avl", "insercao", maior)
    busca_hash = obter_estatistica(grupos, "hash", "busca_existente", maior)
    busca_avl = obter_estatistica(grupos, "avl", "busca_existente", maior)
    lista_hash = obter_estatistica(grupos, "hash", "listagem_codigo", maior)
    lista_avl = obter_estatistica(grupos, "avl", "listagem_codigo", maior)

    speedup_insercao = calcular_speedup(insercao_hash, insercao_avl)
    speedup_busca = calcular_speedup(busca_hash, busca_avl)
    vencedor_listagem = vencedor(lista_hash, lista_avl)

    return "\n".join(
        [
            r"\paragraph{Destaques empíricos.}",
            (
                f"Na maior base avaliada ($n={maior}$), a Hash foi "
                f"{speedup_insercao} mais rápida na inserção "
                f"({formatar_media_desvio(insercao_hash)} contra "
                f"{formatar_media_desvio(insercao_avl)}) e "
                f"{speedup_busca} mais rápida na busca existente "
                f"({formatar_media_desvio(busca_hash)} contra "
                f"{formatar_media_desvio(busca_avl)}). "
                f"Na listagem ordenada, a estrutura mais rápida foi "
                f"\\textbf{{{vencedor_listagem}}} "
                f"({formatar_media_desvio(lista_hash)} para Hash e "
                f"{formatar_media_desvio(lista_avl)} para AVL)."
            ),
        ]
    )


def gerar_tex(linhas: list[dict[str, str]]) -> str:
    tamanhos = descobrir_tamanhos(linhas)
    repeticoes = descobrir_repeticoes(linhas)
    python_version = platform.python_version()
    sistema = platform.platform()

    conteudo = [
        "% Gerado automaticamente por src/experiments/analise_resultados.py",
        f"% Fonte: {ARQUIVO_CSV.as_posix()}",
        f"% Data: {date.today().isoformat()}",
        "",
        r"\subsection{Metodologia experimental}",
        r"\label{sec:metodologia-experimental}",
        "",
        (
            "Os experimentos foram executados com o benchmark em "
            r"\texttt{src/experiments/benchmark.py}, alimentado pelos CSVs "
            r"\texttt{data/produtos\_100.csv}, \texttt{produtos\_1000.csv} e "
            r"\texttt{produtos\_10000.csv}. A leitura dos arquivos permaneceu "
            "fora da medição; em cada cenário, a estrutura é montada previamente "
            "em memória volátil e suas métricas internas são zeradas antes da "
            "operação avaliada."
        ),
        "",
        f"Cada cenário foi repetido {repeticoes} vezes com "
        r"\texttt{SEED = 42} para garantir reprodutibilidade.",
        "",
        (
            f"Ambiente de geração deste relatório: Python {python_version}, "
            f"{sistema}."
        ),
        "",
        (
            r"A Tabela~\ref{tab:cenarios} relaciona cada cenário experimental "
            r"ao fluxo correspondente no sistema de estoque."
        ),
        "",
        gerar_tabela_cenarios(),
        "",
        r"\subsection{Resultados}",
        r"\label{sec:resultados-experimentos}",
        "",
        (
            r"As Tabelas~\ref{tab:tempos-total}, \ref{tab:speedup} e "
            r"\ref{tab:memoria} consolidam o comparativo de desempenho entre "
            r"Tabela Hash e Árvore AVL."
        ),
        "",
        gerar_tabela_tempos(linhas, tamanhos),
        "",
        gerar_tabela_speedup(linhas, tamanhos),
        "",
        gerar_tabela_memoria(linhas, tamanhos),
        "",
        r"\subsection{Métricas estruturais}",
        "",
        (
            r"As Tabelas~\ref{tab:numero-colisoes-insercao}, "
            r"\ref{tab:fator-carga-insercao}, \ref{tab:maior-lista-insercao}, "
            r"\ref{tab:numero-rotacoes-insercao} e "
            r"\ref{tab:altura-arvore-insercao} consolidam indicadores "
            r"coletados durante a inserção completa de cada base, "
            r"complementando a análise de tempo com evidências sobre colisões "
            r"e balanceamento."
        ),
        "",
        gerar_tabela_metricas_estruturais(linhas, tamanhos),
        "",
        r"\subsection{Discussão}",
        r"\label{sec:discussao-experimentos}",
        "",
        *gerar_discussao_narrativa(linhas, tamanhos),
    ]

    return "\n".join(conteudo)


def main() -> None:
    linhas = carregar_csv(ARQUIVO_CSV)
    tex = gerar_tex(linhas)

    ARQUIVO_TEX.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_TEX.write_text(tex, encoding="utf-8")

    print(f"Linhas processadas: {len(linhas)}")
    print(f"Arquivo gerado: {ARQUIVO_TEX}")


if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        raise
