from dataclasses import dataclass
from datetime import date


@dataclass
class Produto:
    codigo_barras: str
    nome: str
    categoria: str
    preco: float
    quantidade: int
    validade: date | None = None

    def __post_init__(self):
        # Código de barras
        if not self.codigo_barras.isdigit():
            raise ValueError("O código de barras deve conter apenas números.")

        # Nome
        if not self.nome.strip():
            raise ValueError("O nome não pode ser vazio.")

        # Categoria
        if not self.categoria.strip():
            raise ValueError("A categoria não pode ser vazia.")

        # Preço
        if self.preco < 0:
            raise ValueError("O preço não pode ser negativo.")

        # Quantidade
        if self.quantidade < 0:
            raise ValueError("A quantidade não pode ser negativa.")