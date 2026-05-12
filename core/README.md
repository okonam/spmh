# 📽️ SPMH — Self Portable Media Hub

**SPMH** é um motor de hub de mídia leve e portátil projetado para transformar instantaneamente qualquer pasta de arquivos de vídeo em uma biblioteca estilo Netflix. 

Este projeto foi criado para ser **Zero-Config**: você o coloca dentro da sua pasta de vídeos, executa o motor, e ele monta dinamicamente um portal com capas, categorias e streaming direto no seu navegador.

---

## 🚀 Como usar

1.  **Clone ou Baixe** este repositório.
2.  **Mova** a pasta do projeto para dentro da sua pasta raiz de vídeos (ou coloque seus vídeos em uma pasta chamada `media` dentro do projeto).
3.  **Execute** o arquivo `LIGAR_SPMH.bat`.
4.  Acesse `http://localhost:8888` no seu navegador.

## ✨ Funcionalidades

- **Escaneamento Recursivo:** Encontra vídeos em todas as subpastas.
- **Categorização Automática:** Usa os nomes das suas pastas como categorias do hub.
- **Geração de Thumbnails:** Cria capas para seus vídeos automaticamente usando FFMPEG.
- **Player Integrado:** Streaming nativo via navegador com suporte a Seek (avançar/retroceder).
- **Design Premium:** Interface inspirada no Netflix, responsiva e moderna.

## 🛠️ Tecnologias

- **Backend:** Python + FastAPI (Streaming e Escaneamento)
- **Frontend:** HTML5 + Tailwind CSS + Alpine.js (Interface reativa sem build)
- **Processamento:** FFMPEG/FFPROBE (Thumbnails e Metadados)

## 🤝 Contribuindo (Open Source)

Este é um projeto de código aberto! Sinta-se à vontade para abrir Issues ou enviar Pull Requests.

**Ideias para o futuro:**
- [ ] Suporte a Legendas (.srt).
- [ ] Integração com APIs de Metadados (IMDb/TMDB).
- [ ] Modo "Cinema" (Fundo escurecido).
- [ ] Suporte a múltiplos usuários.

---
Desenvolvido com ❤️ para a comunidade.
