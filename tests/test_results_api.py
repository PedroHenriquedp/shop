from src.api.server import carregar_resultados_consolidados


def test_consolida_os_resultados_oficiais() -> None:
    dados = carregar_resultados_consolidados()

    assert dados["metodologia"]["repeticoes"] == 30
    assert dados["metodologia"]["bases"] == [100, 1000, 10000]
    assert len(dados["resultados"]) == 42

    insercao_hash = next(
        resultado
        for resultado in dados["resultados"]
        if resultado["estrutura"] == "hash"
        and resultado["cenario"] == "insercao"
        and resultado["tamanho_base"] == 100
    )
    assert insercao_hash["amostras"] == 30
    assert insercao_hash["colisoes_media"] == 21
