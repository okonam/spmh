# Protótipo: Hero Engine (Cinematic)

## Objetivo
Preservar o visual de "exposição dupla" onde o vídeo da direita se funde com o fundo preto da esquerda.

## Especificações Técnicas
1. **Máscara Vertical (`.hero-v-mask`):** Deve ser aplicada a uma `div` que contém o vídeo. Ela usa `linear-gradient(to right, black 60%, transparent 75%)`.
2. **Gradientes de Overlay:**
   - Horizontal: `#0a0a0a` para `transparent`.
   - Vertical (Bottom): `#0a0a0a` para `transparent`.
3. **Tipografia:** Títulos com `font-black tracking-tighter`.

## Como Instalar
- Copiar o bloco `<section>` para a área do Hero no `index.html`.
- Certificar-se de que a `div` do vídeo está com `hero-v-mask`.
