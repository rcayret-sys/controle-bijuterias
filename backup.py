from pathlib import Path
from datetime import datetime
import shutil
from database import BANCO

PASTA_BACKUP = "backups"


def criar_backup():
    origem = Path(BANCO)

    if not origem.exists():
        return False, "Banco de dados não encontrado."

    pasta = Path(PASTA_BACKUP)
    pasta.mkdir(exist_ok=True)

    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = pasta / f"backup_bijuterias_{agora}.db"

    shutil.copy2(origem, destino)

    return True, str(destino)
