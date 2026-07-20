# src/structures/avl_tree.py

from src.models.produto import Produto


class NoAVL:
    def __init__(self, produto: Produto):
        self.produto = produto
        self.esquerda: NoAVL | None = None
        self.direita: NoAVL | None = None
        self.altura = 1


class AVLTree:
    def __init__(self):
        self.raiz: NoAVL | None = None
        self.quantidade_elementos = 0

        # Métricas
        self.numero_comparacoes = 0
        self.numero_rotacoes = 0

    def _altura(self, no: NoAVL | None) -> int:
        if no is None:
            return 0

        return no.altura

    def _atualizar_altura(self, no: NoAVL) -> None:
        no.altura = 1 + max(
            self._altura(no.esquerda),
            self._altura(no.direita)
        )

    def _fator_balanceamento(
        self,
        no: NoAVL | None
    ) -> int:
        if no is None:
            return 0

        return (
            self._altura(no.esquerda)
            - self._altura(no.direita)
        )

    def _rotacao_direita(
        self,
        no_desbalanceado: NoAVL
    ) -> NoAVL:
        nova_raiz = no_desbalanceado.esquerda

        if nova_raiz is None:
            return no_desbalanceado

        subarvore_transferida = nova_raiz.direita

        nova_raiz.direita = no_desbalanceado
        no_desbalanceado.esquerda = subarvore_transferida

        self._atualizar_altura(no_desbalanceado)
        self._atualizar_altura(nova_raiz)

        self.numero_rotacoes += 1

        return nova_raiz

    def _rotacao_esquerda(
        self,
        no_desbalanceado: NoAVL
    ) -> NoAVL:
        nova_raiz = no_desbalanceado.direita

        if nova_raiz is None:
            return no_desbalanceado

        subarvore_transferida = nova_raiz.esquerda

        nova_raiz.esquerda = no_desbalanceado
        no_desbalanceado.direita = subarvore_transferida

        self._atualizar_altura(no_desbalanceado)
        self._atualizar_altura(nova_raiz)

        self.numero_rotacoes += 1

        return nova_raiz

    def inserir(self, produto: Produto) -> bool:
        """
        Insere um produto na árvore.

        Retorna True quando um novo produto é inserido.
        Retorna False quando o código já existe e os dados
        do produto são atualizados.
        """
        produto_existente = self.buscar(
            produto.codigo_barras
        )

        if produto_existente is not None:
            produto_existente.nome = produto.nome
            produto_existente.categoria = produto.categoria
            produto_existente.preco = produto.preco
            produto_existente.quantidade = produto.quantidade
            produto_existente.validade = produto.validade

            return False

        self.raiz = self._inserir(
            self.raiz,
            produto
        )

        self.quantidade_elementos += 1

        return True

    def _inserir(
        self,
        no: NoAVL | None,
        produto: Produto
    ) -> NoAVL:
        if no is None:
            return NoAVL(produto)

        self.numero_comparacoes += 1

        if produto.codigo_barras < no.produto.codigo_barras:
            no.esquerda = self._inserir(
                no.esquerda,
                produto
            )
        else:
            no.direita = self._inserir(
                no.direita,
                produto
            )

        self._atualizar_altura(no)

        fator = self._fator_balanceamento(no)

        # Caso esquerda-esquerda
        if (
            fator > 1
            and no.esquerda is not None
            and produto.codigo_barras
            < no.esquerda.produto.codigo_barras
        ):
            return self._rotacao_direita(no)

        # Caso direita-direita
        if (
            fator < -1
            and no.direita is not None
            and produto.codigo_barras
            > no.direita.produto.codigo_barras
        ):
            return self._rotacao_esquerda(no)

        # Caso esquerda-direita
        if (
            fator > 1
            and no.esquerda is not None
            and produto.codigo_barras
            > no.esquerda.produto.codigo_barras
        ):
            no.esquerda = self._rotacao_esquerda(
                no.esquerda
            )

            return self._rotacao_direita(no)

        # Caso direita-esquerda
        if (
            fator < -1
            and no.direita is not None
            and produto.codigo_barras
            < no.direita.produto.codigo_barras
        ):
            no.direita = self._rotacao_direita(
                no.direita
            )

            return self._rotacao_esquerda(no)

        return no

    def buscar(
        self,
        codigo_barras: str
    ) -> Produto | None:
        """
        Busca um produto pelo código de barras.
        """
        no_atual = self.raiz

        while no_atual is not None:
            self.numero_comparacoes += 1

            if codigo_barras == no_atual.produto.codigo_barras:
                return no_atual.produto

            if codigo_barras < no_atual.produto.codigo_barras:
                no_atual = no_atual.esquerda
            else:
                no_atual = no_atual.direita

        return None

    def remover(
        self,
        codigo_barras: str
    ) -> Produto | None:
        """
        Remove um produto pelo código de barras.

        Retorna o produto removido quando ele existe.
        Retorna None quando o código não é encontrado.
        """
        self.raiz, produto_removido = self._remover(
            self.raiz,
            codigo_barras
        )

        if produto_removido is not None:
            self.quantidade_elementos -= 1

        return produto_removido

    def _menor_no(self, no: NoAVL) -> NoAVL:
        """
        Encontra o nó com o menor código de barras
        em uma subárvore.
        """
        no_atual = no

        while no_atual.esquerda is not None:
            no_atual = no_atual.esquerda

        return no_atual

    def _remover(
        self,
        no: NoAVL | None,
        codigo_barras: str
    ) -> tuple[NoAVL | None, Produto | None]:
        """
        Remove recursivamente um nó e rebalanceia a árvore.

        Retorna:
        - a nova raiz da subárvore;
        - o produto removido ou None.
        """
        if no is None:
            return None, None

        self.numero_comparacoes += 1

        produto_removido: Produto | None = None

        if codigo_barras < no.produto.codigo_barras:
            no.esquerda, produto_removido = self._remover(
                no.esquerda,
                codigo_barras
            )

        elif codigo_barras > no.produto.codigo_barras:
            no.direita, produto_removido = self._remover(
                no.direita,
                codigo_barras
            )

        else:
            produto_removido = no.produto

            # Caso 1: nó sem filho à esquerda
            if no.esquerda is None:
                return no.direita, produto_removido

            # Caso 2: nó sem filho à direita
            if no.direita is None:
                return no.esquerda, produto_removido

            # Caso 3: nó com dois filhos
            sucessor = self._menor_no(no.direita)

            no.produto = sucessor.produto

            no.direita, _ = self._remover(
                no.direita,
                sucessor.produto.codigo_barras
            )

        if produto_removido is None:
            return no, None

        self._atualizar_altura(no)

        fator = self._fator_balanceamento(no)

        # Caso esquerda-esquerda
        if (
            fator > 1
            and self._fator_balanceamento(no.esquerda) >= 0
        ):
            return (
                self._rotacao_direita(no),
                produto_removido
            )

        # Caso esquerda-direita
        if (
            fator > 1
            and self._fator_balanceamento(no.esquerda) < 0
        ):
            if no.esquerda is not None:
                no.esquerda = self._rotacao_esquerda(
                    no.esquerda
                )

            return (
                self._rotacao_direita(no),
                produto_removido
            )

        # Caso direita-direita
        if (
            fator < -1
            and self._fator_balanceamento(no.direita) <= 0
        ):
            return (
                self._rotacao_esquerda(no),
                produto_removido
            )

        # Caso direita-esquerda
        if (
            fator < -1
            and self._fator_balanceamento(no.direita) > 0
        ):
            if no.direita is not None:
                no.direita = self._rotacao_direita(
                    no.direita
                )

            return (
                self._rotacao_esquerda(no),
                produto_removido
            )

        return no, produto_removido

    def listar_em_ordem(self) -> list[Produto]:
        """
        Retorna os produtos ordenados pelo código de barras.
        """
        produtos: list[Produto] = []

        self._listar_em_ordem(
            self.raiz,
            produtos
        )

        return produtos

    def _listar_em_ordem(
        self,
        no: NoAVL | None,
        produtos: list[Produto]
    ) -> None:
        if no is None:
            return

        self._listar_em_ordem(
            no.esquerda,
            produtos
        )

        produtos.append(no.produto)

        self._listar_em_ordem(
            no.direita,
            produtos
        )

    def obter_altura(self) -> int:
        return self._altura(self.raiz)

    def obter_metricas(self) -> dict:
        return {
            "quantidade_elementos": self.quantidade_elementos,
            "altura_arvore": self.obter_altura(),
            "numero_comparacoes": self.numero_comparacoes,
            "numero_rotacoes": self.numero_rotacoes,
        }

    def reiniciar_metricas(self) -> None:
        """
        Reinicia as métricas sem alterar os produtos armazenados.
        """
        self.numero_comparacoes = 0
        self.numero_rotacoes = 0

    def __len__(self) -> int:
        return self.quantidade_elementos

    def __contains__(
        self,
        codigo_barras: str
    ) -> bool:
        return self.buscar(codigo_barras) is not None