import sqlite3
import streamlit as st

from database import criar_tabelas
from configuracoes import carregar_configuracoes, salvar_configuracoes
from categorias import (
    carregar_categorias,
    salvar_categoria,
    atualizar_categoria,
    categoria_em_uso,
    excluir_categoria,
)
from produtos import salvar_produto, atualizar_produto, carregar_produtos
from estoque import (
    registrar_entrada,
    carregar_entradas,
    registrar_ajuste_estoque,
    carregar_ajustes,
)
from vendas import registrar_venda, carregar_vendas, cancelar_venda
from backup import criar_backup
from utils import (
    moeda_br,
    formatar_colunas_moeda,
    exportar_csv,
    grafico_barras,
    aplicar_filtro_texto,
    preparar_datas_vendas,
)

criar_tabelas()
nome_programa, icone_programa = carregar_configuracoes()

st.set_page_config(
    page_title=nome_programa,
    page_icon=icone_programa,
    layout="wide"
)

st.title(f"{icone_programa} {nome_programa}")
st.divider()

opcoes_menu = [
    "Dashboard",
    "Cadastro de Produtos",
    "Editar Produto",
    "Gerenciar Categorias",
    "Entrada de Estoque",
    "Ajuste de Estoque",
    "Produtos Cadastrados",
    "Registrar Venda",
    "Cancelar Venda",
    "Histórico de Vendas",
    "Histórico de Entradas",
    "Histórico de Ajustes",
    "Backup e Exportação",
    "Configurações"
]

pagina = st.selectbox(
    "Menu",
    opcoes_menu,
    index=0
)

st.divider()

if pagina == "Dashboard":

    df_produtos = carregar_produtos()
    df_vendas = carregar_vendas(incluir_canceladas=False)
    df_vendas = preparar_datas_vendas(df_vendas)

    st.subheader("Dashboard")

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        categoria_filtro = st.selectbox(
            "Filtrar categoria",
            ["Todas"] + sorted(df_produtos["Categoria"].dropna().unique().tolist()) if not df_produtos.empty else ["Todas"]
        )

    with col_f2:
        status_produto_filtro = st.selectbox(
            "Filtrar produtos",
            ["Ativo", "Todos", "Inativo"]
        )

    anos_disponiveis = (
        sorted(df_vendas["Ano"].dropna().astype(int).unique().tolist(), reverse=True)
        if not df_vendas.empty and "Ano" in df_vendas.columns
        else []
    )

    meses_nomes = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }

    with col_f3:
        ano_filtro = st.selectbox(
            "Ano das vendas",
            ["Todos"] + anos_disponiveis
        )

    with col_f4:
        mes_filtro_nome = st.selectbox(
            "Mês das vendas",
            ["Todos"] + list(meses_nomes.values())
        )

    produtos_filtrados = df_produtos.copy()

    if not produtos_filtrados.empty:
        if categoria_filtro != "Todas":
            produtos_filtrados = produtos_filtrados[produtos_filtrados["Categoria"] == categoria_filtro]

        if status_produto_filtro != "Todos":
            produtos_filtrados = produtos_filtrados[produtos_filtrados["Status"] == status_produto_filtro]

    vendas_filtradas = df_vendas.copy()

    if not vendas_filtradas.empty:
        if categoria_filtro != "Todas":
            vendas_filtradas = vendas_filtradas[vendas_filtradas["Categoria"] == categoria_filtro]

        if ano_filtro != "Todos":
            vendas_filtradas = vendas_filtradas[vendas_filtradas["Ano"] == int(ano_filtro)]

        if mes_filtro_nome != "Todos":
            mes_numero = [k for k, v in meses_nomes.items() if v == mes_filtro_nome][0]
            vendas_filtradas = vendas_filtradas[vendas_filtradas["Mês"] == mes_numero]

    total_produtos = len(produtos_filtrados)
    total_estoque = int(produtos_filtrados["Estoque"].sum()) if not produtos_filtrados.empty else 0
    valor_estoque = float((produtos_filtrados["Custo"] * produtos_filtrados["Estoque"]).sum()) if not produtos_filtrados.empty else 0
    total_vendas = float(vendas_filtradas["Valor Total"].sum()) if not vendas_filtradas.empty else 0
    lucro_total = float(vendas_filtradas["Lucro Total"].sum()) if not vendas_filtradas.empty else 0
    quantidade_vendida = int(vendas_filtradas["Quantidade"].sum()) if not vendas_filtradas.empty else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Produtos", total_produtos)

    with col2:
        st.metric("Itens em estoque", total_estoque)

    with col3:
        st.metric("Custo em estoque", moeda_br(valor_estoque))

    with col4:
        st.metric("Itens vendidos", quantidade_vendida)

    with col5:
        st.metric("Total vendido", moeda_br(total_vendas))

    with col6:
        st.metric("Lucro total", moeda_br(lucro_total))

    st.divider()

    if not produtos_filtrados.empty:
        estoque_categoria = (
            produtos_filtrados
            .groupby("Categoria", as_index=False)["Estoque"]
            .sum()
            .sort_values("Estoque", ascending=False)
        )

        grafico_barras(
            estoque_categoria,
            "Categoria",
            "Estoque",
            "Estoque por categoria",
            formato_y=",.0f"
        )

    if not vendas_filtradas.empty:
        vendas_mes = (
            vendas_filtradas
            .groupby("Mês/Ano", as_index=False)["Valor Total"]
            .sum()
        )

        grafico_barras(
            vendas_mes,
            "Mês/Ano",
            "Valor Total",
            "Valor vendido por mês",
            formato_y=",.2f"
        )

        vendas_produto = (
            vendas_filtradas
            .groupby("Produto", as_index=False)["Quantidade"]
            .sum()
            .sort_values("Quantidade", ascending=False)
            .head(10)
        )

        grafico_barras(
            vendas_produto,
            "Produto",
            "Quantidade",
            "Produtos mais vendidos",
            formato_y=",.0f"
        )

        vendas_valor_produto = (
            vendas_filtradas
            .groupby("Produto", as_index=False)["Valor Total"]
            .sum()
            .sort_values("Valor Total", ascending=False)
            .head(10)
        )

        grafico_barras(
            vendas_valor_produto,
            "Produto",
            "Valor Total",
            "Top 10 produtos por valor vendido",
            formato_y=",.2f"
        )

        with st.expander("Ver vendas consideradas no dashboard"):
            df_dash = vendas_filtradas.drop(
                columns=["CanceladaNum", "Data_dt", "Ano", "Mês"],
                errors="ignore"
            )

            df_dash = formatar_colunas_moeda(
                df_dash,
                ["Preço Unitário", "Custo Unitário", "Valor Total", "Lucro Total"]
            )

            st.dataframe(df_dash, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma venda encontrada para os filtros selecionados.")


elif pagina == "Cadastro de Produtos":

    st.subheader("Cadastro de Produtos")

    df_categorias = carregar_categorias(apenas_ativas=True)

    if df_categorias.empty:
        st.warning("Cadastre pelo menos uma categoria ativa antes de cadastrar produtos.")
    else:
        categorias = df_categorias["Categoria"].tolist()

        with st.form("form_produto", clear_on_submit=True):

            codigo = st.text_input("Código")
            descricao = st.text_input("Descrição")
            categoria = st.selectbox("Categoria", categorias)

            col1, col2, col3 = st.columns(3)

            with col1:
                custo = st.number_input("Custo do item", min_value=0.0, format="%.2f")

            with col2:
                preco = st.number_input("Preço de venda", min_value=0.0, format="%.2f")

            with col3:
                estoque = st.number_input("Quantidade em estoque", min_value=0, step=1)

            salvar = st.form_submit_button("Salvar produto")

        if salvar:
            if descricao.strip() == "":
                st.error("Informe a descrição do produto.")
            else:
                salvar_produto(codigo, descricao, categoria, custo, preco, estoque)
                st.success("Produto cadastrado com sucesso!")

elif pagina == "Editar Produto":

    st.subheader("Editar Produto")

    df_produtos = carregar_produtos()

    if df_produtos.empty:
        st.info("Nenhum produto cadastrado ainda.")
    else:
        df_produtos["Produto Exibição"] = (
            df_produtos["ID"].astype(str)
            + " - "
            + df_produtos["Descrição"]
            + " | Estoque: "
            + df_produtos["Estoque"].astype(str)
            + " | "
            + df_produtos["Status"]
        )

        produto_escolhido = st.selectbox("Selecione o produto", df_produtos["Produto Exibição"])

        linha_produto = df_produtos[df_produtos["Produto Exibição"] == produto_escolhido].iloc[0]

        df_categorias = carregar_categorias(apenas_ativas=True)
        categorias = df_categorias["Categoria"].tolist()

        categoria_atual = linha_produto["Categoria"]

        if categoria_atual not in categorias:
            categorias.append(categoria_atual)

        indice_categoria = categorias.index(categoria_atual) if categoria_atual in categorias else 0

        status_opcoes = ["Ativo", "Inativo"]
        status_atual = linha_produto["Status"]
        indice_status = status_opcoes.index(status_atual)

        with st.form("form_editar_produto"):

            codigo = st.text_input("Código", value=str(linha_produto["Código"]))
            descricao = st.text_input("Descrição", value=str(linha_produto["Descrição"]))

            col_a, col_b = st.columns(2)

            with col_a:
                categoria = st.selectbox("Categoria", categorias, index=indice_categoria)

            with col_b:
                status = st.selectbox("Status", status_opcoes, index=indice_status)

            col1, col2, col3 = st.columns(3)

            with col1:
                custo = st.number_input(
                    "Custo do item",
                    min_value=0.0,
                    value=float(linha_produto["Custo"]),
                    format="%.2f"
                )

            with col2:
                preco = st.number_input(
                    "Preço de venda",
                    min_value=0.0,
                    value=float(linha_produto["Preço Venda"]),
                    format="%.2f"
                )

            with col3:
                estoque = st.number_input(
                    "Quantidade em estoque",
                    min_value=0,
                    value=int(linha_produto["Estoque"]),
                    step=1
                )

            atualizar = st.form_submit_button("Atualizar produto")

        if atualizar:
            if descricao.strip() == "":
                st.error("Informe a descrição do produto.")
            else:
                ativo = 1 if status == "Ativo" else 0

                atualizar_produto(
                    int(linha_produto["ID"]),
                    codigo,
                    descricao,
                    categoria,
                    custo,
                    preco,
                    estoque,
                    ativo
                )

                st.success("Produto atualizado com sucesso!")

elif pagina == "Gerenciar Categorias":

    st.subheader("Gerenciar Categorias")

    st.markdown("### Nova categoria")

    with st.form("form_nova_categoria", clear_on_submit=True):
        nova_categoria = st.text_input("Nome da categoria")
        salvar_cat = st.form_submit_button("Salvar categoria")

    if salvar_cat:
        if nova_categoria.strip() == "":
            st.error("Informe o nome da categoria.")
        else:
            try:
                salvar_categoria(nova_categoria.strip())
                st.success("Categoria cadastrada com sucesso!")
            except sqlite3.IntegrityError:
                st.error("Essa categoria já existe.")

    st.divider()

    st.markdown("### Editar categoria")

    df_categorias = carregar_categorias()

    if df_categorias.empty:
        st.info("Nenhuma categoria cadastrada.")
    else:
        df_categorias["Exibição"] = (
            df_categorias["ID"].astype(str)
            + " - "
            + df_categorias["Categoria"]
            + " | "
            + df_categorias["Status"]
        )

        categoria_escolhida = st.selectbox(
            "Selecione uma categoria",
            df_categorias["Exibição"]
        )

        linha_categoria = df_categorias[
            df_categorias["Exibição"] == categoria_escolhida
        ].iloc[0]

        status_opcoes = ["Ativo", "Inativo"]
        status_atual = linha_categoria["Status"]
        indice_status = status_opcoes.index(status_atual)

        with st.form("form_editar_categoria"):
            nome_editado = st.text_input(
                "Nome",
                value=str(linha_categoria["Categoria"])
            )

            status_editado = st.selectbox(
                "Status",
                status_opcoes,
                index=indice_status
            )

            col1, col2 = st.columns(2)

            with col1:
                atualizar_cat = st.form_submit_button("Atualizar categoria")

            with col2:
                excluir_cat = st.form_submit_button("Excluir categoria")

        if atualizar_cat:
            if nome_editado.strip() == "":
                st.error("Informe o nome da categoria.")
            else:
                try:
                    atualizar_categoria(
                        int(linha_categoria["ID"]),
                        str(linha_categoria["Categoria"]),
                        nome_editado.strip(),
                        1 if status_editado == "Ativo" else 0
                    )

                    st.success("Categoria atualizada com sucesso!")
                except sqlite3.IntegrityError:
                    st.error("Já existe uma categoria com esse nome.")

        if excluir_cat:
            nome_categoria = str(linha_categoria["Categoria"])

            if categoria_em_uso(nome_categoria):
                st.warning(
                    "Esta categoria está em uso por produto(s). "
                    "Para preservar o histórico, inative em vez de excluir."
                )
            else:
                excluir_categoria(int(linha_categoria["ID"]))
                st.success("Categoria excluída com sucesso!")

    st.divider()

    df_exibicao = carregar_categorias()

    if not df_exibicao.empty:
        st.dataframe(
            df_exibicao.drop(columns=["AtivoNum"]),
            use_container_width=True,
            hide_index=True
        )

elif pagina == "Entrada de Estoque":

    st.subheader("Entrada de Estoque")

    df_produtos = carregar_produtos()

    if df_produtos.empty:
        st.warning("Cadastre produtos primeiro.")
    else:
        df_produtos_ativos = df_produtos[df_produtos["Status"] == "Ativo"].copy()

        if df_produtos_ativos.empty:
            st.warning("Não há produtos ativos para entrada de estoque.")
        else:
            df_produtos_ativos["Produto Exibição"] = (
                df_produtos_ativos["Descrição"]
                + " | Estoque atual: "
                + df_produtos_ativos["Estoque"].astype(str)
            )

            with st.form("form_entrada", clear_on_submit=True):

                produto_escolhido = st.selectbox("Produto", df_produtos_ativos["Produto Exibição"])

                quantidade = st.number_input("Quantidade de entrada", min_value=1, step=1)

                observacao = st.text_input("Observação", placeholder="Ex: Compra fornecedor XPTO")

                registrar = st.form_submit_button("Registrar entrada")

            if registrar:
                linha_produto = df_produtos_ativos[
                    df_produtos_ativos["Produto Exibição"] == produto_escolhido
                ].iloc[0]

                registrar_entrada(int(linha_produto["ID"]), quantidade, observacao)

                st.success("Entrada registrada com sucesso!")

elif pagina == "Ajuste de Estoque":

    st.subheader("Ajuste de Estoque")

    df_produtos = carregar_produtos()

    if df_produtos.empty:
        st.warning("Cadastre produtos primeiro.")
    else:
        df_produtos["Produto Exibição"] = (
            df_produtos["ID"].astype(str)
            + " - "
            + df_produtos["Descrição"]
            + " | Estoque atual: "
            + df_produtos["Estoque"].astype(str)
        )

        with st.form("form_ajuste_estoque"):

            produto_escolhido = st.selectbox("Produto", df_produtos["Produto Exibição"])

            tipo_ajuste = st.selectbox(
                "Tipo de ajuste",
                ["Entrada", "Saída", "Definir estoque final"]
            )

            quantidade = st.number_input(
                "Quantidade",
                min_value=0,
                step=1
            )

            motivo = st.text_input(
                "Motivo",
                placeholder="Ex: inventário, perda, correção de lançamento"
            )

            ajustar = st.form_submit_button("Registrar ajuste")

        if ajustar:
            if motivo.strip() == "":
                st.error("Informe o motivo do ajuste.")
            else:
                linha_produto = df_produtos[
                    df_produtos["Produto Exibição"] == produto_escolhido
                ].iloc[0]

                sucesso, mensagem = registrar_ajuste_estoque(
                    int(linha_produto["ID"]),
                    tipo_ajuste,
                    int(quantidade),
                    motivo.strip()
                )

                if sucesso:
                    st.success(mensagem)
                else:
                    st.error(mensagem)

elif pagina == "Produtos Cadastrados":

    st.subheader("Produtos Cadastrados")

    df_produtos = carregar_produtos()

    if df_produtos.empty:
        st.info("Nenhum produto cadastrado ainda.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            filtro_status = st.selectbox("Filtrar por status", ["Todos", "Ativo", "Inativo"])

        with col2:
            filtro_categoria = st.selectbox(
                "Filtrar por categoria",
                ["Todas"] + sorted(df_produtos["Categoria"].dropna().unique().tolist())
            )

        with col3:
            busca = st.text_input("Buscar")

        if filtro_status != "Todos":
            df_produtos = df_produtos[df_produtos["Status"] == filtro_status]

        if filtro_categoria != "Todas":
            df_produtos = df_produtos[df_produtos["Categoria"] == filtro_categoria]

        df_produtos = aplicar_filtro_texto(
            df_produtos,
            busca,
            ["Código", "Descrição", "Categoria", "Status"]
        )

        df_exibicao = df_produtos.drop(columns=["AtivoNum"])

        df_exibicao = formatar_colunas_moeda(
            df_exibicao,
            ["Custo", "Preço Venda", "Lucro Unitário"]
        )

        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

        st.download_button(
            "Exportar produtos para CSV",
            data=exportar_csv(df_exibicao, ["Custo", "Preço Venda", "Lucro Unitário"]),
            file_name="produtos.csv",
            mime="text/csv"
        )

elif pagina == "Registrar Venda":

    st.subheader("Registrar Venda")

    df_produtos = carregar_produtos()

    if df_produtos.empty:
        st.warning("Cadastre pelo menos um produto antes de registrar vendas.")
    else:
        produtos_disponiveis = df_produtos[
            (df_produtos["Estoque"] > 0) &
            (df_produtos["Status"] == "Ativo")
        ].copy()

        if produtos_disponiveis.empty:
            st.warning("Não há produtos ativos com estoque disponível.")
        else:
            produtos_disponiveis["Produto Exibição"] = (
                produtos_disponiveis["Descrição"]
                + " | Estoque: "
                + produtos_disponiveis["Estoque"].astype(str)
                + " | "
                + produtos_disponiveis["Preço Venda"].map(moeda_br)
            )

            with st.form("form_venda", clear_on_submit=True):

                produto_escolhido = st.selectbox("Produto", produtos_disponiveis["Produto Exibição"])

                quantidade = st.number_input("Quantidade vendida", min_value=1, step=1)

                vender = st.form_submit_button("Registrar venda")

            if vender:
                linha_produto = produtos_disponiveis[
                    produtos_disponiveis["Produto Exibição"] == produto_escolhido
                ].iloc[0]

                sucesso, mensagem = registrar_venda(int(linha_produto["ID"]), quantidade)

                if sucesso:
                    st.success(mensagem)
                else:
                    st.error(mensagem)

elif pagina == "Cancelar Venda":

    st.subheader("Cancelar Venda")

    df_vendas = carregar_vendas(incluir_canceladas=True)

    if df_vendas.empty:
        st.info("Nenhuma venda registrada ainda.")
    else:
        vendas_ativas = df_vendas[df_vendas["Status"] == "Ativa"].copy()

        if vendas_ativas.empty:
            st.info("Não há vendas ativas para cancelar.")
        else:
            vendas_ativas["Exibição"] = (
                "ID "
                + vendas_ativas["ID"].astype(str)
                + " | "
                + vendas_ativas["Data"].astype(str)
                + " | "
                + vendas_ativas["Produto"]
                + " | Qtde: "
                + vendas_ativas["Quantidade"].astype(str)
                + " | "
                + vendas_ativas["Valor Total"].map(moeda_br)
            )

            with st.form("form_cancelar_venda"):

                venda_escolhida = st.selectbox("Venda", vendas_ativas["Exibição"])

                motivo = st.text_input("Motivo do cancelamento")

                cancelar = st.form_submit_button("Cancelar venda")

            if cancelar:
                if motivo.strip() == "":
                    st.error("Informe o motivo do cancelamento.")
                else:
                    linha_venda = vendas_ativas[
                        vendas_ativas["Exibição"] == venda_escolhida
                    ].iloc[0]

                    sucesso, mensagem = cancelar_venda(int(linha_venda["ID"]), motivo.strip())

                    if sucesso:
                        st.success(mensagem)
                    else:
                        st.error(mensagem)

elif pagina == "Histórico de Vendas":

    st.subheader("Histórico de Vendas")

    df_vendas = carregar_vendas(incluir_canceladas=True)

    if df_vendas.empty:
        st.info("Nenhuma venda registrada ainda.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            filtro_status = st.selectbox("Filtrar status", ["Todas", "Ativa", "Cancelada"])

        with col2:
            filtro_categoria = st.selectbox(
                "Filtrar categoria",
                ["Todas"] + sorted(df_vendas["Categoria"].dropna().unique().tolist())
            )

        with col3:
            busca = st.text_input("Buscar")

        if filtro_status != "Todas":
            df_vendas = df_vendas[df_vendas["Status"] == filtro_status]

        if filtro_categoria != "Todas":
            df_vendas = df_vendas[df_vendas["Categoria"] == filtro_categoria]

        df_vendas = aplicar_filtro_texto(
            df_vendas,
            busca,
            ["Código", "Produto", "Categoria", "Status", "Motivo Cancelamento"]
        )

        df_exibicao = df_vendas.drop(columns=["CanceladaNum"])

        df_exibicao = formatar_colunas_moeda(
            df_exibicao,
            ["Preço Unitário", "Custo Unitário", "Valor Total", "Lucro Total"]
        )

        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

        st.download_button(
            "Exportar vendas para CSV",
            data=exportar_csv(df_exibicao, ["Preço Unitário", "Custo Unitário", "Valor Total", "Lucro Total"]),
            file_name="vendas.csv",
            mime="text/csv"
        )

elif pagina == "Histórico de Entradas":

    st.subheader("Histórico de Entradas")

    df_entradas = carregar_entradas()

    if df_entradas.empty:
        st.info("Nenhuma entrada registrada ainda.")
    else:
        busca = st.text_input("Buscar")

        df_entradas = aplicar_filtro_texto(
            df_entradas,
            busca,
            ["Código", "Produto", "Observação"]
        )

        st.dataframe(df_entradas, use_container_width=True, hide_index=True)

        st.download_button(
            "Exportar entradas para CSV",
            data=exportar_csv(df_entradas),
            file_name="entradas.csv",
            mime="text/csv"
        )

elif pagina == "Histórico de Ajustes":

    st.subheader("Histórico de Ajustes")

    df_ajustes = carregar_ajustes()

    if df_ajustes.empty:
        st.info("Nenhum ajuste registrado ainda.")
    else:
        busca = st.text_input("Buscar")

        df_ajustes = aplicar_filtro_texto(
            df_ajustes,
            busca,
            ["Código", "Produto", "Tipo", "Motivo"]
        )

        st.dataframe(df_ajustes, use_container_width=True, hide_index=True)

        st.download_button(
            "Exportar ajustes para CSV",
            data=exportar_csv(df_ajustes),
            file_name="ajustes_estoque.csv",
            mime="text/csv"
        )

elif pagina == "Backup e Exportação":

    st.subheader("Backup e Exportação")

    st.markdown("### Backup do banco de dados")

    if st.button("Criar backup agora"):
        sucesso, mensagem = criar_backup()

        if sucesso:
            st.success(f"Backup criado: {mensagem}")
        else:
            st.error(mensagem)

    st.divider()

    st.markdown("### Exportações rápidas")

    df_produtos = carregar_produtos()
    df_vendas = carregar_vendas(incluir_canceladas=True)
    df_entradas = carregar_entradas()
    df_ajustes = carregar_ajustes()

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "Baixar produtos CSV",
            data=exportar_csv(
                df_produtos.drop(columns=["AtivoNum"]) if not df_produtos.empty else df_produtos,
                ["Custo", "Preço Venda", "Lucro Unitário"]
            ),
            file_name="produtos.csv",
            mime="text/csv"
        )

        st.download_button(
            "Baixar entradas CSV",
            data=exportar_csv(df_entradas),
            file_name="entradas.csv",
            mime="text/csv"
        )

    with col2:
        st.download_button(
            "Baixar vendas CSV",
            data=exportar_csv(
                df_vendas.drop(columns=["CanceladaNum"]) if not df_vendas.empty else df_vendas,
                ["Preço Unitário", "Custo Unitário", "Valor Total", "Lucro Total"]
            ),
            file_name="vendas.csv",
            mime="text/csv"
        )

        st.download_button(
            "Baixar ajustes CSV",
            data=exportar_csv(df_ajustes),
            file_name="ajustes_estoque.csv",
            mime="text/csv"
        )

elif pagina == "Configurações":

    st.subheader("Configurações do Sistema")

    icones = [
        "💍",
        "💎",
        "🛍️",
        "📦",
        "🧾",
        "🌸",
        "✨",
        "🏷️",
        "👑",
        "🎁"
    ]

    if icone_programa in icones:
        indice_icone = icones.index(icone_programa)
    else:
        indice_icone = 0

    with st.form("form_configuracoes"):

        novo_nome = st.text_input(
            "Nome do programa",
            value=nome_programa
        )

        novo_icone = st.selectbox(
            "Ícone do programa",
            icones,
            index=indice_icone
        )

        salvar_config = st.form_submit_button("Salvar configurações")

    if salvar_config:
        if novo_nome.strip() == "":
            st.error("Informe o nome do programa.")
        else:
            salvar_configuracoes(
                novo_nome.strip(),
                novo_icone
            )

            st.success("Configurações salvas com sucesso! Clique em Rerun ou atualize a página para refletir na aba do navegador.")

    st.info(f"Prévia: {novo_icone} {novo_nome}")
