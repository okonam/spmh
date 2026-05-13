# Especificação Técnica: SPMH Cinematic Hero

Este documento descreve as definições visuais e lógicas do componente **Hero** do SPMH Hub para garantir a preservação da estética "Cinematic Double Exposure" em futuras atualizações.

## 1. Estética Visual
O Hero utiliza uma técnica de **exposição dupla** onde o vídeo de fundo se funde suavemente com o conteúdo e o fundo preto do portal.

### CSS de Mascaramento (Core)
```css
/* Máscara de transição para o container do Hero */
.hero-mask { 
    background: linear-gradient(to right, rgba(10,10,10,0) 0%, rgba(10,10,10,0) 60%, #0a0a0a 75%, rgba(10,10,10,0) 90%, rgba(10,10,10,0) 100%); 
}

/* Máscara aplicada diretamente ao elemento <video> */
.hero-v-mask { 
    -webkit-mask-image: linear-gradient(to right, black 60%, transparent 75%);
    mask-image: linear-gradient(to right, black 60%, transparent 75%);
}
```

## 2. Estrutura HTML
O Hero deve ocupar aproximadamente **95vh** e possuir uma sobreposição de gradientes para garantir a legibilidade do texto.

```html
<section class="relative h-[95vh] w-full overflow-hidden bg-black">
    <!-- Gradientes de Fusão -->
    <div class="absolute inset-0 bg-gradient-to-r from-[#0a0a0a] via-[#0a0a0a]/80 to-transparent z-10"></div>
    <div class="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-transparent to-transparent z-10"></div>
    
    <!-- Video Background (Alinhado à direita) -->
    <div class="absolute right-0 top-0 w-3/4 h-full hero-v-mask">
         <video :src="'/api/stream/' + hero.id" autoplay muted loop class="w-full h-full object-cover"></video>
    </div>

    <!-- Conteúdo (Alinhado à esquerda) -->
    <div class="relative z-20 max-w-[1800px] mx-auto px-10 flex flex-col justify-center h-full">
        <!-- Título em Black Tighter, Subtítulo em Italic Light -->
    </div>
</section>
```

## 3. Lógica de Transição (Alpine.js)
- **Rotatividade:** O Hero alterna entre os vídeos da `featuredList` a cada 10 segundos.
- **featuredList:** Seleciona aleatoriamente 5 vídeos da biblioteca no carregamento inicial (`fetchData`).
- **Pausa Inteligente:** O temporizador de troca do Hero pausa quando o player está aberto ou o usuário está pesquisando.

## 4. Tipografia e Cores
- **Fonte Principal:** 'Outfit', sans-serif.
- **Títulos:** `font-black tracking-tighter uppercase`.
- **Cor de Acento:** Red-600 (`#dc2626`).
- **Fundo Base:** `#0a0a0a`.
