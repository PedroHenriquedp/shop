# src/structures/hash_table.py

from src.models.produto import Produto


class HashTable:
    """
    Tabela Hash para armazenamento de produtos.

    A chave utilizada é o código de barras do produto.
    As colisões são tratadas por encadeamento separado:
    cada posição da tabela contém uma lista de produtos.
    """

    def __init__(self, tamanho: int = 101):
        if tamanho <= 0:
            raise ValueError("O tamanho da tabela deve ser maior que zero.")

        self.tamanho = tamanho

        # Cada posição da tabela contém uma lista.
        self.tabela: list[list[Produto]] = [
            [] for _ in range(tamanho)
        ]

        self.quantidade_elementos = 0

        # Métricas
        self.numero_colisoes = 0
        self.numero_comparacoes = 0

    def _funcao_hash(self, codigo_barras: str) -> int:
        """
        Calcula a posição do produto na tabela.

        O código de barras é convertido em inteiro e o resto
        da divisão pelo tamanho da tabela define o índice.
        """
        if not codigo_barras.isdigit():
            raise ValueError(
                "O código de barras deve conter apenas números."
            )

        return int(codigo_barras) % self.tamanho

    def inserir(self, produto: Produto) -> bool:
        """
        Insere um produto na tabela.

        Retorna True quando o produto é inserido.

        Caso já exista um produto com o mesmo código de barras,
        seus dados são atualizados e o método retorna False.
        """
        indice = self._funcao_hash(produto.codigo_barras)
        lista = self.tabela[indice]

        for produto_existente in lista:
            self.numero_comparacoes += 1

            if (
                produto_existente.codigo_barras
                == produto.codigo_barras
            ):
                produto_existente.nome = produto.nome
                produto_existente.categoria = produto.categoria
                produto_existente.preco = produto.preco
                produto_existente.quantidade = produto.quantidade
                produto_existente.validade = produto.validade

                return False

        # Há colisão quando a posição já contém outro produto.
        if len(lista) > 0:
            self.numero_colisoes += 1

        lista.append(produto)
        self.quantidade_elementos += 1

        return True

    def buscar(self, codigo_barras: str) -> Produto | None:
        """
        Busca um produto pelo código de barras.

        Retorna o produto quando encontrado.
        Retorna None caso o produto não exista.
        """
        indice = self._funcao_hash(codigo_barras)
        lista = self.tabela[indice]

        for produto in lista:
            self.numero_comparacoes += 1

            if produto.codigo_barras == codigo_barras:
                return produto

        return None

    def remover(self, codigo_barras: str) -> Produto | None:
        """
        Remove um produto pelo código de barras.

        Retorna o produto removido.
        Retorna None caso o produto não exista.
        """
        indice = self._funcao_hash(codigo_barras)
        lista = self.tabela[indice]

        for posicao, produto in enumerate(lista):
            self.numero_comparacoes += 1

            if produto.codigo_barras == codigo_barras:
                produto_removido = lista.pop(posicao)
                self.quantidade_elementos -= 1

                return produto_removido

        return None

    def atualizar_quantidade(
        self,
        codigo_barras: str,
        nova_quantidade: int
    ) -> bool:
        """
        Atualiza a quantidade disponível de um produto.

        Retorna True quando a atualização é realizada.
        Retorna False quando o produto não é encontrado.
        """
        if nova_quantidade < 0:
            raise ValueError(
                "A quantidade não pode ser negativa."
            )

        produto = self.buscar(codigo_barras)

        if produto is None:
            return False

        produto.quantidade = nova_quantidade
        return True

    def listar_produtos(self) -> list[Produto]:
        """
        Retorna todos os produtos armazenados na tabela.
        """
        produtos = []

        for lista in self.tabela:
            produtos.extend(lista)

        return produtos

    def fator_carga(self) -> float:
        """
        Calcula o fator de carga da tabela.

        Fator de carga = quantidade de elementos / tamanho da tabela.
        """
        return self.quantidade_elementos / self.tamanho

    def maior_lista(self) -> int:
        """
        Retorna o tamanho da maior lista de colisões da tabela.
        """
        return max(
            len(lista) for lista in self.tabela
        )

    def quantidade_posicoes_ocupadas(self) -> int:
        """
        Retorna quantas posições da tabela possuem produtos.
        """
        return sum(
            1 for lista in self.tabela if len(lista) > 0
        )

    def obter_metricas(self) -> dict:
        """
        Retorna as principais métricas da tabela Hash.
        """
        return {
            "tamanho_tabela": self.tamanho,
            "quantidade_elementos": self.quantidade_elementos,
            "posicoes_ocupadas":
                self.quantidade_posicoes_ocupadas(),
            "fator_carga": self.fator_carga(),
            "numero_colisoes": self.numero_colisoes,
            "numero_comparacoes": self.numero_comparacoes,
            "maior_lista": self.maior_lista(),
        }

    def reiniciar_metricas(self) -> None:
        """
        Reinicia as métricas utilizadas nos experimentos.

        Os produtos armazenados não são removidos.
        """
        self.numero_colisoes = 0
        self.numero_comparacoes = 0

    def __len__(self) -> int:
        """
        Permite utilizar len(tabela_hash).
        """
        return self.quantidade_elementos

    def __contains__(self, codigo_barras: str) -> bool:
        """
        Permite verificar a existência de um produto usando:

        codigo_barras in tabela_hash
        """
        return self.buscar(codigo_barras) is not None