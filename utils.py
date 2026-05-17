import pandas as pd
import streamlit as st
import altair as alt


def moeda_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_colunas_moeda(df, colunas):
    df_formatado = df.copy()
    for coluna in colunas:
        if coluna in df_formatado.columns:
            df_formatado[coluna] = df_formatado[coluna].apply(moeda_br)
    return df_formatado


def numero_br(valor):
    try:
        return f"{float(valor):.2f}".replace(".", ",")
    except (ValueError, TypeError):
        return valor


def preparar_csv_brasil(df, colunas_valor=None):
    df_csv = df.copy()

    if colunas_valor is None:
        colunas_valor = []

    for coluna in colunas_valor:
        if coluna in df_csv.columns:
            df_csv[coluna] = df_csv[coluna].apply(numero_br)

    return df_csv


def exportar_csv(df, colunas_valor=None):
    df_csv = preparar_csv_brasil(df, colunas_valor)
    return df_csv.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")


def grafico_barras(df, coluna_x, coluna_y, titulo, formato_y=",.0f"):
    if df.empty:
        st.info(f"Sem dados para exibir em: {titulo}")
        return

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{coluna_x}:N", sort="-y", title=""),
            y=alt.Y(f"{coluna_y}:Q", title="", axis=alt.Axis(format=formato_y)),
            tooltip=[
                alt.Tooltip(f"{coluna_x}:N", title=coluna_x),
                alt.Tooltip(f"{coluna_y}:Q", title=coluna_y, format=formato_y),
            ],
        )
        .properties(
            title=titulo,
            height=360
        )
    )

    st.altair_chart(chart, use_container_width=True)


def aplicar_filtro_texto(df, texto, colunas):
    if df.empty or texto.strip() == "":
        return df

    texto = texto.strip().lower()
    mascara = False

    for coluna in colunas:
        if coluna in df.columns:
            mascara = mascara | df[coluna].astype(str).str.lower().str.contains(texto, na=False)

    return df[mascara]


def preparar_datas_vendas(df):
    if df.empty or "Data" not in df.columns:
        return df

    df_datas = df.copy()
    df_datas["Data_dt"] = pd.to_datetime(
        df_datas["Data"],
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce"
    )
    df_datas["Ano"] = df_datas["Data_dt"].dt.year
    df_datas["Mês"] = df_datas["Data_dt"].dt.month
    df_datas["Mês/Ano"] = df_datas["Data_dt"].dt.strftime("%m/%Y")

    return df_datas
