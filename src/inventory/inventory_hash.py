# src/inventory/inventory_hash.py

from src.models.produto import Produto
from src.structures.hash_table import HashTable


class InventoryHash:
    def __init__(self, tamanho_tabela: int = 101):
        """
        Cria um sistema de estoque baseado em tabela Hash.

        Parâmetros:
        tamanho_tabela: quantidade de posições da tabela Hash.
        """
        self.estrutura = HashTable(
            tamanho=tamanho_tabela
        )

    def cadastrar_produto(self, produto: Produto) -> bool:
        """
        Cadastra um produto no estoque.

        Retorna True quando um novo produto é inserido.
        Retorna False quando o produto já existe e seus dados
        são atualizados.
        """
        return self.estrutura.inserir(produto)

    def buscar_produto(
        self,
        codigo_barras: str
    ) -> Produto | None:
        """
        Busca um produto pelo código de barras.
        """
        return self.estrutura.buscar(codigo_barras)

    def remover_produto(
        self,
        codigo_barras: str
    ) -> Produto | None:
        """
        Remove um produto pelo código de barras.

        Retorna o produto removido.
        Retorna None se o produto não existir.
        """
        return self.estrutura.remover(codigo_barras)

    def registrar_entrada(
        self,
        codigo_barras: str,
        quantidade: int
    ) -> bool:
        """
        Acrescenta unidades ao estoque de um produto.

        Retorna False se o produto não existir.
        """
        if quantidade <= 0:
            raise ValueError(
                "A quantidade de entrada deve ser maior que zero."
            )

        produto = self.buscar_produto(codigo_barras)

        if produto is None:
            return False

        produto.quantidade += quantidade

        return True

    def registrar_venda(
        self,
        codigo_barras: str,
        quantidade: int
    ) -> bool:
        """
        Retira unidades do estoque após uma venda.

        Retorna False quando:
        - o produto não existe;
        - não há quantidade suficiente em estoque.
        """
        if quantidade <= 0:
            raise ValueError(
                "A quantidade vendida deve ser maior que zero."
            )

        produto = self.buscar_produto(codigo_barras)

        if produto is None:
            return False

        if produto.quantidade < quantidade:
            return False

        produto.quantidade -= quantidade

        return True

    def atualizar_preco(
        self,
        codigo_barras: str,
        novo_preco: float
    ) -> bool:
        """
        Atualiza o preço de um produto existente.
        """
        if novo_preco < 0:
            raise ValueError(
                "O preço não pode ser negativo."
            )

        produto = self.buscar_produto(codigo_barras)

        if produto is None:
            return False

        produto.preco = novo_preco

        return True

    def consultar_quantidade(
        self,
        codigo_barras: str
    ) -> int | None:
        """
        Retorna a quantidade disponível do produto.

        Retorna None se o produto não existir.
        """
        produto = self.buscar_produto(codigo_barras)

        if produto is None:
            return None

        return produto.quantidade

    def listar_produtos(self) -> list[Produto]:
        """
        Retorna todos os produtos armazenados na tabela Hash.

        A ordem depende da distribuição dos produtos na tabela.
        """
        return self.estrutura.listar_produtos()

    def listar_produtos_por_nome(self) -> list[Produto]:
        """
        Retorna os produtos ordenados alfabeticamente pelo nome.
        """
        return sorted(
            self.listar_produtos(),
            key=lambda produto: produto.nome.lower()
        )

    def listar_produtos_por_validade(self) -> list[Produto]:
        """
        Retorna os produtos ordenados pela validade.

        Produtos sem validade ficam no final.
        """
        return sorted(
            self.listar_produtos(),
            key=lambda produto: (
                produto.validade is None,
                produto.validade
            )
        )

    def obter_metricas(self) -> dict:
        """
        Retorna as métricas internas da tabela Hash.
        """
        return self.estrutura.obter_metricas()

    def reiniciar_metricas(self) -> None:
        """
        Reinicia as métricas sem apagar os produtos.
        """
        self.estrutura.reiniciar_metricas()

    def __len__(self) -> int:
        """
        Permite usar len(estoque).
        """
        return len(self.estrutura)