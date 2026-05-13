# Protótipo: Diagnostics HUD (Tecla D)

## Objetivo
Ter uma visão clara de por que um vídeo não abriu ou de onde ele está vindo, sem precisar olhar o console do navegador.

## O que deve ser exibido
1. **ID do Vídeo:** Para conferir no banco de dados.
2. **Estado do Buffer:** Para saber se o vídeo está travado por internet/disco.
3. **Erros de Rede:** Mostrar se deu erro 404 ou 500 no streaming.

## Como Aplicar
- Inserir o bloco de código do HUD dentro do container do player em `index.html`.
- Vincular os campos de texto às variáveis reais do Alpine.js (`$refs.player`).
