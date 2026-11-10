RISCOS = {"VERMELHO": 0, "AMARELO": 1, "VERDE": 2}

EMOJI = {"VERMELHO": "🔴", "AMARELO": "🟡", "VERDE": "🟢"}
SEM_PREFERENCIA = "Normal"

def normalizar_risco(valor) -> str:
    chave = str(valor).strip().upper()
    if chave not in RISCOS:
        raise ValueError(f"Risco inválido: {valor!r}. Use VERMELHO, AMARELO ou VERDE.")
    return chave
