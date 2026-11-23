"""Modo exercício: ALVO=gabarito faz os testes usarem a resolução completa (pasta gabarito/)."""
import os
import sys
from pathlib import Path

_alvo = os.environ.get("ALVO")
if _alvo:
    sys.path.insert(0, str(Path(__file__).resolve().parent / _alvo))
    # Importa JÁ o pacote: com `nucleo` fixado em sys.modules, todo `nucleo.x` vem do gabarito,
    # mesmo que o pytest recoloque a pasta raiz na frente do sys.path depois.
    import nucleo  # noqa: E402,F401
