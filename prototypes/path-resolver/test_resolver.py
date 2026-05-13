import os
import hashlib

# MOCK DATA
MOCK_LIBRARY = {
    "fake_id_123": {
        "title": "Video Teste",
        "path": "JDOWNLOADER/Ind Rodrigues.mp4" # Caminho relativo ao VIDEO_ROOT
    }
}

def resolve_path(video_id, current_root):
    """
    Simula a inteligência do motor de busca do SPMH.
    """
    video_info = MOCK_LIBRARY.get(video_id)
    if not video_info:
        return None, "ID não encontrado"
    
    relative_path = video_info['path']
    # Tenta construir o caminho absoluto com base no ROOT atual (ex: Y:\DOWNLOADS)
    absolute_path = os.path.join(current_root, relative_path)
    
    if os.path.exists(absolute_path):
        return absolute_path, "Sucesso (Caminho Direto)"
    
    # FALLBACK: Se não achar no caminho direto, faz uma busca recursiva pelo nome do arquivo
    filename = os.path.basename(relative_path)
    for root, dirs, files in os.walk(current_root):
        if filename in files:
            found_path = os.path.join(root, filename)
            return found_path, f"Sucesso (Encontrado via Busca Recursiva em: {root})"
            
    return None, "Erro: Arquivo não localizado no drive atual"

# TESTE
if __name__ == "__main__":
    current_drive_root = "Y:\\DOWNLOADS" # Simulando que estamos no Y: agora
    print(f"--- TESTANDO RESOLUÇÃO DE CAMINHO NO DRIVE {current_drive_root} ---")
    
    path, msg = resolve_path("fake_id_123", current_drive_root)
    print(f"Resultado: {msg}")
    print(f"Caminho Final: {path}")
