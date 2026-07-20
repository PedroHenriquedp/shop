# Resultados experimentais e geração do LaTeX

Este diretório concentra os artefatos da **seção 3** do artigo (`main.tex`):
os dados brutos do benchmark e o fragmento LaTeX gerado automaticamente.

Use este guia quando alguém estiver rodando experimentos e outra pessoa
estiver editando o relatório no **Prism** (ou outro editor LaTeX) em paralelo.

---

## Visão geral do fluxo

```text
src/main.py  ──►  results/resultados.csv
                         │
                         ▼
         src/experiments/analise_resultados.py
                         │
                         ▼
         results/resultados_experimentos.tex
                         │
                         ▼
              main.tex  (\input{results/resultados_experimentos.tex})
                         │
                         ▼
                    main.pdf
```

| Arquivo | Quem edita | Descrição |
|---------|------------|-----------|
| `resultados.csv` | gerado por `src/main.py` | Dados brutos de cada execução |
| `resultados_experimentos.tex` | **gerado pelo script** | Subseções 3.1–3.4, tabelas e discussão |
| `main.tex` | equipe do artigo (Prism) | Introdução da seção 3, conclusão, bibliografia |

**Regra principal:** não edite `resultados_experimentos.tex` à mão.
Qualquer alteração nesse arquivo será sobrescrita na próxima execução do script.
Ajustes de texto, tabelas ou números devem ser feitos em
`src/experiments/analise_resultados.py` (ou rodando o benchmark de novo).

---

## Pré-requisitos

- **Python 3.10+** (stdlib apenas; o script não instala pacotes externos)
- **`results/resultados.csv`** atualizado — gerado por:

```powershell
# Na raiz do repositório (C:\Users\vinic\shop)
python -m src.main
```

O benchmark usa os CSVs em `data/produtos_100.csv`, `produtos_1000.csv` e
`produtos_10000.csv`, com 30 repetições e `SEED = 42`.

---

## Como usar `analise_resultados.py`

### Comando

```powershell
# Na raiz do repositório
python src/experiments/analise_resultados.py
```

Saída esperada:

```text
Linhas processadas: 1260
Arquivo gerado: C:\Users\vinic\shop\results\resultados_experimentos.tex
```

### O que o script faz

1. Lê `results/resultados.csv`
2. Agrupa por `estrutura`, `cenario` e `tamanho_base`
3. Calcula média e desvio padrão das repetições
4. Gera o fragmento LaTeX com:
   - **3.1 Metodologia experimental** — texto + Tabela de cenários
   - **3.2 Resultados** — tempos, speedup (AVL/Hash) e memória pico
   - **3.3 Métricas estruturais** — colisões, fator de carga, rotações, altura
   - **3.4 Discussão** — narrativa com números sincronizados ao CSV

### Entrada esperada (`resultados.csv`)

Colunas obrigatórias (mesmo cabeçalho produzido por `src/main.py`):

```text
estrutura, cenario, tamanho_base, repeticao, quantidade_operacoes,
operacoes_sucesso, tempo_total_segundos, tempo_medio_segundos,
memoria_pico_bytes, quantidade_elementos, numero_comparacoes,
numero_colisoes, fator_carga, maior_lista, numero_rotacoes, altura_arvore
```

Cenários reconhecidos: `insercao`, `busca_existente`, `busca_inexistente`,
`remocao`, `vendas`, `operacoes_mistas`, `listagem_codigo`.

Estruturas: `hash` e `avl`.

---

## Compilar o PDF (Prism ou terminal)

O `main.tex` inclui o fragmento gerado:

```latex
\input{results/resultados_experimentos.tex}
```

### No Prism

1. Abra `main.tex` na raiz do projeto
2. Compile normalmente (pdfLaTeX)
3. Se as referências `\ref{tab:...}` aparecerem como `??`, compile **duas vezes**

### No terminal (MiKTeX, Windows)

```powershell
cd C:\Users\vinic\shop
& "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode main.tex
& "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe" -interaction=nonstopmode main.tex
```

O pacote `float` (`[H]` nas tabelas) e `\FloatBarrier` antes da Conclusão
evitam que tabelas “flutuem” para depois da seção 4.

---

## Trabalho em paralelo (benchmark + Prism)

### Pessoa A — experimentos

```powershell
python -m src.main
python src/experiments/analise_resultados.py
git add results/resultados.csv results/resultados_experimentos.tex
git commit -m "Atualiza resultados experimentais"
```

### Pessoa B — artigo no Prism

- Editar **`main.tex`** (introdução da seção 3, conclusão, refs bibliográficas)
- **Não** editar `resultados_experimentos.tex`
- Após pull com CSV novo: rodar só `analise_resultados.py` e recompilar

### Ordem recomendada após `git pull`

```powershell
python src/experiments/analise_resultados.py
# Recompilar main.tex no Prism
```

Assim os números da discussão e das tabelas ficam alinhados ao CSV mais recente.

---

## Quando rodar o script

| Situação | Ação |
|----------|------|
| Novo `resultados.csv` após benchmark | Rodar `analise_resultados.py` |
| Alteração em `analise_resultados.py` | Rodar o script e recompilar `main.tex` |
| Só mudou texto em `main.tex` | Recompilar; script **não** necessário |
| Conflito no Git em `resultados_experimentos.tex` | Aceitar versão regenerada pelo script |

---

## Erros comuns

### `Arquivo não encontrado: .../results/resultados.csv`

O benchmark ainda não foi executado. Rode `python -m src.main` primeiro.

### Tabelas ou números desatualizados no PDF

1. Confirme a data no cabeçalho de `resultados_experimentos.tex`
2. Regere com `python src/experiments/analise_resultados.py`
3. Compile `main.tex` duas vezes

### Referências `??` no PDF

Compile o LaTeX mais de uma vez (referências cruzadas entre tabelas e discussão).

### `Linhas processadas` muito abaixo do esperado

Para 3 bases × 30 repetições × 7 cenários × 2 estruturas = **1260 linhas**.
Valores menores indicam benchmark incompleto ou CSV truncado.

---

## Onde alterar o conteúdo gerado

| Objetivo | Arquivo |
|----------|---------|
| Mudar texto das subseções, captions ou discussão | `src/experiments/analise_resultados.py` |
| Mudar cenários ou métricas coletadas | `src/experiments/benchmark.py` |
| Mudar repetições ou bases | `src/main.py` |
| Mudar intro da seção 3 ou conclusão | `main.tex` |

Depois de editar o gerador, sempre regenere e recompile:

```powershell
python src/experiments/analise_resultados.py
```
