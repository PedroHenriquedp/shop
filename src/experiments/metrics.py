# src/experiments/metrics.py

from dataclasses import dataclass
from time import perf_counter
import tracemalloc
from typing import Any, Callable


@dataclass
class ResultadoMedicao:
    tempo_total: float
    tempo_medio: float
    memoria_pico_bytes: int
    quantidade_operacoes: int
    resultado: Any = None


def medir_execucao(
    funcao: Callable,
    quantidade_operacoes: int,
    *args,
    **kwargs
) -> ResultadoMedicao:
    """
    Executa uma função e mede tempo e pico de memória.

    A leitura do CSV deve acontecer antes desta função,
    para não misturar o custo de entrada de dados com
    o custo das estruturas.
    """
    if quantidade_operacoes < 0:
        raise ValueError(
            "A quantidade de operações não pode ser negativa."
        )

    tracemalloc.start()

    inicio = perf_counter()

    resultado = funcao(*args, **kwargs)

    fim = perf_counter()

    _, memoria_pico = tracemalloc.get_traced_memory()

    tracemalloc.stop()

    tempo_total = fim - inicio

    tempo_medio = (
        tempo_total / quantidade_operacoes
        if quantidade_operacoes > 0
        else 0.0
    )

    return ResultadoMedicao(
        tempo_total=tempo_total,
        tempo_medio=tempo_medio,
        memoria_pico_bytes=memoria_pico,
        quantidade_operacoes=quantidade_operacoes,
        resultado=resultado
    )