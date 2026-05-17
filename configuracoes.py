from database import executar, obter_um

def carregar_configuracoes():
    config = obter_um("""SELECT nome_programa, icone_programa FROM configuracoes WHERE id = 1""")
    if config is None:
        return "Controle de Bijuterias", "💍"
    return config[0], config[1]

def salvar_configuracoes(nome_programa, icone_programa):
    executar("""UPDATE configuracoes SET nome_programa=:nome_programa, icone_programa=:icone_programa WHERE id=1""", {"nome_programa":nome_programa,"icone_programa":icone_programa})
