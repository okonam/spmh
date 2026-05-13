# Protótipo: Modal Player

## Objetivo
Mudar a forma como o vídeo é exibido: de tela cheia absoluta para um **Modal Centralizado** (estilo Sovrano-Flix).

## Como Instalar (Manual para o Antigravity)
1. **HTML Estrutura:** Substituir o `template x-if="playing"` do arquivo principal pelo bloco contido em `demo.html`.
2. **Alpine.js Logic:**
   - Remover a lógica de `showIntro` no método `playVideo`.
   - Adicionar o `this.$nextTick` para disparar o `p.play()` imediatamente após o modal aparecer.
3. **CSS:** Garantir que as classes de `backdrop-blur-2xl` e o gradiente `from-black/80` estejam presentes.

## Benefícios
- Maior estabilidade em navegadores Chrome/Edge.
- Evita o erro de "topo sumindo".
- Sensação de portal premium sem interrupções de tela cheia forçada.
