# Benchmark de estoque: Hash vs AVL

Este projeto compara uma tabela Hash e uma árvore AVL usando o mesmo conjunto de produtos e a metodologia apresentada no artigo. A fonte oficial dos resultados é `results/resultados.csv`, gerado pelo experimento em `src/`.

## Metodologia oficial

- Bases CSV com 100, 1.000 e 10.000 produtos;
- sete cenários: inserção, busca existente, busca inexistente, remoção, vendas, operações mistas e listagem ordenada;
- 30 repetições por cenário, base e estrutura;
- tempos, memória de pico, comparações, colisões, fator de carga, rotações e altura;
- total esperado: 1.260 linhas no arquivo de resultados.

O frontend não executa um segundo benchmark. Ele apenas consulta a API e apresenta as médias e desvios das mesmas medições usadas no artigo.

## Requisito

Use Python 3.10 ou superior. O Docker Compose já utiliza Python 3.11.

## Executar os experimentos

```bash
python -m src.main
python src/experiments/analise_resultados.py
```

O primeiro comando atualiza `results/resultados.csv`. O segundo gera o fragmento LaTeX usado pelo artigo.

## Visualização local

```bash
python -m src.api.server
```

Abra `http://localhost:8000/frontend/`. Selecione a base e o cenário para comparar Hash e AVL. A API está em `http://localhost:8000/api/resultados`.

Na aba **Teste ao vivo**, informe de 1 a 100.000 produtos e execute uma rodada. Ela roda os mesmos sete cenários uma vez, mostra os tempos daquela execução e substitui o resultado anterior. Para 100, 1.000 e 10.000 produtos, usa os CSVs oficiais; nas demais quantidades, gera uma base temporária de e-commerce em memória.

## Testes

```bash
python -m pytest
```

## Docker Compose

```bash
docker compose up --build
```

Abra `http://localhost:8000/frontend/`. O container lê os CSVs e resultados da pasta local; para atualizar os números exibidos, execute o experimento antes de subir o serviço.
