import os
import glob

def scan_for_subtitles(video_path):
    """
    Simula a lógica do SPMH para encontrar legendas.
    Busca arquivos .srt ou .vtt com o mesmo nome do vídeo na mesma pasta.
    """
    base_name = os.path.splitext(video_path)[0]
    # Busca por: VideoName.srt, VideoName.pt-BR.srt, VideoName.eng.srt, etc.
    subtitle_files = glob.glob(f"{base_name}*.srt") + glob.glob(f"{base_name}*.vtt")
    
    tracks = []
    for sub in subtitle_files:
        lang = "Unknown"
        if ".pt" in sub.lower() or ".br" in sub.lower(): lang = "Portuguese"
        elif ".en" in sub.lower(): lang = "English"
        
        tracks.append({
            "label": lang,
            "src": f"/api/subtitles/{os.path.basename(sub)}",
            "srclang": lang[:2].lower()
        })
    
    return tracks

# TESTE DE FOGO
if __name__ == "__main__":
    video = "X:/OKONAM/Videos - Filmes/O corvo.mp4"
    print(f"--- ESCANEANDO LEGENDAS PARA: {os.path.basename(video)} ---")
    
    # Simulando que existem legendas na pasta
    found = scan_for_subtitles(video)
    
    if not found:
        print("Nenhuma legenda encontrada. (Dica: coloque um arquivo 'O corvo.srt' na mesma pasta para testar)")
    else:
        for t in found:
            print(f"Legenda detectada: {t['label']} -> {t['src']}")
