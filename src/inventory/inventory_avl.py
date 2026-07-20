# src/inventory/inventory_avl.py

from src.models.produto import Produto
from src.structures.avl_tree import AVLTree


class InventoryAVL:
    def __init__(self):
        self.estrutura = AVLTree()

    def cadastrar_produto(self, produto: Produto) -> bool:
        """
        Cadastra um produto no estoque.

        Retorna True se um novo produto foi inserido.
        Retorna False se já existia um produto com o mesmo
        código de barras e seus dados foram atualizados.
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
        - não há quantidade suficiente.
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
        Retorna a quantidade disponível.

        Retorna None se o produto não existir.
        """
        produto = self.buscar_produto(codigo_barras)

        if produto is None:
            return None

        return produto.quantidade

    def listar_produtos(self) -> list[Produto]:
        """
        Retorna todos os produtos ordenados
        pelo código de barras.
        """
        return self.estrutura.listar_em_ordem()

    def listar_produtos_por_nome(self) -> list[Produto]:
        """
        Retorna os produtos ordenados pelo nome.

        Como a AVL está organizada pelo código de barras,
        é necessário ordenar a lista pelo nome.
        """
        return sorted(
            self.listar_produtos(),
            key=lambda produto: produto.nome.lower()
        )

    def listar_produtos_por_validade(self) -> list[Produto]:
        """
        Retorna os produtos ordenados pela validade.

        Produtos sem validade ficam no final da lista.
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
        Retorna as métricas da árvore AVL.
        """
        return self.estrutura.obter_metricas()

    def reiniciar_metricas(self) -> None:
        """
        Reinicia as métricas sem remover os produtos.
        """
        self.estrutura.reiniciar_metricas()

    def __len__(self) -> int:
        return len(self.estrutura)