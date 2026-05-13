# Protótipo: Path Resolver (Auto-Cura)

## Objetivo
Garantir que os vídeos toquem mesmo se você mover a pasta do drive `C:` para o `Y:` ou um pendrive.

## Como funciona
1. **Indexação Relativa:** O banco de dados salva apenas o caminho a partir da raiz da mídia (ex: `Pasta/Video.mp4`).
2. **Reconstrução Dinâmica:** No momento do play, o Python descobre onde ele está rodando (`VIDEO_ROOT`) e cola o caminho relativo na frente.
3. **Fallback Recursivo:** Se o arquivo mudou de subpasta, o sistema faz uma busca rápida pelo nome do arquivo.

## Como Aplicar ao SPMH
- Integrar a função `resolve_path` no endpoint `/api/stream/` do `main.py`.
