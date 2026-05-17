import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

BANCO_LOCAL = "sqlite:///bijuterias.db"


def obter_database_url():
    try:
        return st.secrets.get("DATABASE_URL", BANCO_LOCAL)
    except Exception:
        return BANCO_LOCAL


@st.cache_resource
def criar_engine_cache(database_url):
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if database_url.startswith("postgresql://"):
        return create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=2,
            pool_recycle=1800,
        )

    return create_engine(database_url)


def criar_engine():
    return criar_engine_cache(obter_database_url())


def limpar_cache_dados():
    st.cache_data.clear()


def banco_postgres():
    return criar_engine().url.get_backend_name().startswith("postgresql")


def executar(sql, parametros=None, limpar_cache=True):
    engine = criar_engine()

    with engine.begin() as conn:
        conn.execute(text(sql), parametros or {})

    if limpar_cache:
        limpar_cache_dados()


@st.cache_data(ttl=20, show_spinner=False)
def ler_df_cache(sql, parametros_tuple):
    parametros = dict(parametros_tuple)
    engine = criar_engine()

    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=parametros)


def ler_df(sql, parametros=None):
    parametros = parametros or {}
    parametros_tuple = tuple(sorted(parametros.items()))
    return ler_df_cache(sql, parametros_tuple)


@st.cache_data(ttl=20, show_spinner=False)
def obter_um_cache(sql, parametros_tuple):
    parametros = dict(parametros_tuple)
    engine = criar_engine()

    with engine.connect() as conn:
        return conn.execute(text(sql), parametros).fetchone()


def obter_um(sql, parametros=None):
    parametros = parametros or {}
    parametros_tuple = tuple(sorted(parametros.items()))
    return obter_um_cache(sql, parametros_tuple)


def criar_tabelas():
    engine = criar_engine()

    if engine.url.get_backend_name().startswith("postgresql"):
        criar_tabelas_postgres(engine)
    else:
        criar_tabelas_sqlite(engine)


def criar_tabelas_postgres(engine):
    with engine.begin() as conn:

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY,
                nome_programa TEXT,
                icone_programa TEXT
            )
        """))

        conn.execute(text("""
            INSERT INTO configuracoes (
                id,
                nome_programa,
                icone_programa
            )
            VALUES (1, 'Controle de Bijuterias', '💍')
            ON CONFLICT (id) DO NOTHING
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS categorias (
                id SERIAL PRIMARY KEY,
                nome TEXT UNIQUE,
                ativo INTEGER DEFAULT 1
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS produtos (
                id SERIAL PRIMARY KEY,
                codigo TEXT,
                descricao TEXT NOT NULL,
                categoria TEXT,
                custo DOUBLE PRECISION DEFAULT 0,
                preco DOUBLE PRECISION DEFAULT 0,
                lucro DOUBLE PRECISION DEFAULT 0,
                estoque INTEGER DEFAULT 0,
                ativo INTEGER DEFAULT 1
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS vendas (
                id SERIAL PRIMARY KEY,
                produto_id INTEGER,
                data_venda TEXT,
                quantidade INTEGER,
                preco_unitario DOUBLE PRECISION,
                custo_unitario DOUBLE PRECISION,
                valor_total DOUBLE PRECISION,
                lucro_total DOUBLE PRECISION,
                cancelada INTEGER DEFAULT 0,
                data_cancelamento TEXT,
                motivo_cancelamento TEXT
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS entradas_estoque (
                id SERIAL PRIMARY KEY,
                produto_id INTEGER,
                data_entrada TEXT,
                quantidade INTEGER,
                observacao TEXT
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ajustes_estoque (
                id SERIAL PRIMARY KEY,
                produto_id INTEGER,
                data_ajuste TEXT,
                tipo_ajuste TEXT,
                quantidade INTEGER,
                estoque_anterior INTEGER,
                estoque_novo INTEGER,
                motivo TEXT
            )
        """))

        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos (categoria)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_produtos_ativo ON produtos (ativo)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_vendas_produto_id ON vendas (produto_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_vendas_cancelada ON vendas (cancelada)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_entradas_produto_id ON entradas_estoque (produto_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_ajustes_produto_id ON ajustes_estoque (produto_id)"))

        qtd = conn.execute(text("SELECT COUNT(*) FROM categorias")).scalar()

        if qtd == 0:
            for categoria in ["Brinco", "Colar", "Pulseira", "Anel", "Outro"]:
                conn.execute(
                    text("INSERT INTO categorias (nome, ativo) VALUES (:nome, 1)"),
                    {"nome": categoria}
                )


def criar_tabelas_sqlite(engine):
    with engine.begin() as conn:

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY,
                nome_programa TEXT,
                icone_programa TEXT
            )
        """))

        conn.execute(text("""
            INSERT OR IGNORE INTO configuracoes (
                id,
                nome_programa,
                icone_programa
            )
            VALUES (1, 'Controle de Bijuterias', '💍')
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE,
                ativo INTEGER DEFAULT 1
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT,
                descricao TEXT NOT NULL,
                categoria TEXT,
                custo REAL DEFAULT 0,
                preco REAL DEFAULT 0,
                lucro REAL DEFAULT 0,
                estoque INTEGER DEFAULT 0,
                ativo INTEGER DEFAULT 1
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER,
                data_venda TEXT,
                quantidade INTEGER,
                preco_unitario REAL,
                custo_unitario REAL,
                valor_total REAL,
                lucro_total REAL,
                cancelada INTEGER DEFAULT 0,
                data_cancelamento TEXT,
                motivo_cancelamento TEXT
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS entradas_estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER,
                data_entrada TEXT,
                quantidade INTEGER,
                observacao TEXT
            )
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ajustes_estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER,
                data_ajuste TEXT,
                tipo_ajuste TEXT,
                quantidade INTEGER,
                estoque_anterior INTEGER,
                estoque_novo INTEGER,
                motivo TEXT
            )
        """))

        qtd = conn.execute(text("SELECT COUNT(*) FROM categorias")).scalar()

        if qtd == 0:
            for categoria in ["Brinco", "Colar", "Pulseira", "Anel", "Outro"]:
                conn.execute(
                    text("INSERT INTO categorias (nome, ativo) VALUES (:nome, 1)"),
                    {"nome": categoria}
                )
