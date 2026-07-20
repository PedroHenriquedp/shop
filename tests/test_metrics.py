from src.experiments.metrics import medir_execucao


def somar_numeros(numeros):
    return sum(numeros)


def test_medir_execucao():
    numeros = [1, 2, 3, 4, 5]

    medicao = medir_execucao(
        somar_numeros,
        len(numeros),
        numeros
    )

    assert medicao.resultado == 15
    assert medicao.tempo_total >= 0
    assert medicao.tempo_medio >= 0
    assert medicao.memoria_pico_bytes >= 0
    assert medicao.quantidade_operacoes == 5


def test_medir_execucao_sem_operacoes():
    medicao = medir_execucao(
        lambda: None,
        0
    )

    assert medicao.tempo_medio == 0