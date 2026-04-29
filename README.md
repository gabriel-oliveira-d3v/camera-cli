# 🎨 Webcam to Color ASCII Art

**Transforme sua webcam em arte ASCII colorida no terminal, em tempo real!**

Este projeto captura o vídeo da sua câmera e o converte quadro a quadro em uma representação ASCII **colorida**, utilizando códigos ANSI True Color para preservar as cores originais. Escolha entre diversas paletas de caracteres, ajuste automático ao tamanho do terminal e controles simples por teclado.

---

## 🌟 Demonstração


*Execute o programa em um terminal compatível com True Color e aponte sua webcam para algo colorido. A mágica acontece!*


**Transforme sua webcam em arte ASCII colorida no terminal, em tempo real!**

Este projeto captura o vídeo da sua câmera e o converte quadro a quadro em uma representação ASCII **colorida**, utilizando códigos ANSI True Color para preservar as cores originais. Escolha entre diversas paletas de caracteres, ajuste automático ao tamanho do terminal e controles simples por teclado.

Exemplo (saída fictícia sem cores):

```
...
█▓▒░ @%#+=-:.     .:-=+#%▓█
@%#+=-:.    ░▒▓█    █▓▒░   .:-=+#%
...

```

---

## 🚀 Funcionalidades

- 🎥 **Conversão em tempo real:** O feed da webcam é processado quadro a quadro, exibindo arte ASCII fluida.
- 🌈 **Cores True Color:** Cada caractere recebe a cor RGB exata do pixel original (ou a mais próxima possível, usando 24 bits ANSI).
- 🎭 **Múltiplas paletas de caracteres:** Escolha entre 14 paletas, incluindo:
  - `Binary` (0 e 1)
  - `Medium set` (clássica: `@%#*+=-:. `)
  - `Single block`, `Solid block`, `Minimalist`
  - `Alphabetic`, `Alphanumeric`, `Arrow`, `Math Symbols`, `Numerical` e mais.
- 🔄 **Troca de paleta ao vivo:** Pressione `P` durante a execução para alternar entre as paletas.
- 📐 **Ajuste automático ao terminal:** A largura da arte se adapta ao número de colunas disponíveis, com correção opcional de offset (padrão 4 caracteres a menos).
- 🕹️ **Controles interativos:**
  - `Q` ou `ESC` → sair
  - `P` → próxima paleta
  - `H` → ajuda
- ⚡ **Alto desempenho:** Processamento otimizado com NumPy e controle de FPS, mantendo o uso de CPU baixo.
- 🖥️ **Multiplataforma:** Compatível com Windows, Linux e macOS.

---

## 📋 Pré‑requisitos

- **Python 3.7** ou superior
- **Webcam funcional** (integrada ou USB)
- **Terminal compatível com True Color** para uma experiência completa (exemplos: Windows Terminal, iTerm2, GNOME Terminal, Alacritty, Kitty). Se seu terminal não suportar True Color, as cores podem não aparecer ou serem reduzidas a 16/256 cores.
- Bibliotecas Python: `opencv-python`, `numpy` (`shutil` é nativa)

---

## 🔧 Instalação

Clone este repositório e instale as dependências:

```bash
git clone https://github.com/seu-usuario/webcam-ascii-art.git
cd webcam-ascii-art
pip install opencv-python numpy
```

📦 Se preferir, utilize um ambiente virtual (venv) para isolar as dependências.

---

🎮 Como Usar

1. Abra um terminal que suporte True Color (recomendamos Windows Terminal no Windows, iTerm2 no macOS, ou seu terminal Linux favorito com suporte a 24 bits).
2. Maximize a janela do terminal para melhor efeito.
3. Execute o programa:

```bash
python camera.py
```

1. No menu inicial, digite o número da paleta desejada (ex: 4 para "Medium set") e pressione Enter.
2. Controles durante a exibição:

Tecla Ação
P Alternar para a próxima paleta
Q ou ESC Sair do programa
H Exibir ajuda rápida

Argumentos de linha de comando

Você pode personalizar o offset da primeira linha (caso seu terminal mostre a arte com um pequeno recuo):

```bash
python camera.py --offset 4   # padrão
```

Se o desalinhamento for diferente, ajuste o número.

---

✨ Personalização

Adicionar novas paletas

Edite o arquivo camera.py e insira uma nova entrada no dicionário PALETTES:

```python
PALETTES = {
    ...,
    "15. Nova paleta": "ABC123",   # caracteres do escuro ao claro
}
```

Ajustar a taxa de quadros

No loop principal, a variável target_fps = 30 controla a suavidade. Aumente ou diminua conforme a capacidade do seu hardware.

Alterar o fator de proporção

A conversão de altura usa um fator de 0.55 para compensar a proporção largura/altura dos caracteres no terminal. Se os caracteres parecerem achatados ou alongados, experimente modificar o valor na função frame_to_ascii_vectorized.

---

⚠️ Limitações e Soluções

· Cores não aparecem: verifique se seu terminal suporta True Color (24 bits). A sequência ANSI usada é \033[38;2;R;G;Bm. Você pode testar com: echo -e "\033[38;2;255;0;0mTeste\033[0m". Se falhar, tente outro terminal.
· Desempenho reduzido: em resoluções muito altas ou computadores mais lentos, reduza o FPS alvo (target_fps) ou limite a largura mínima na função get_terminal_width.
· Webcam não encontrada: o código usa cv2.VideoCapture(0). Se sua câmera for outro dispositivo, altere o índice (ex: 1) ou verifique permissões de acesso à câmera.
· Terminal piscando: isso pode ocorrer em alguns sistemas. O programa já usa \033[H para reposicionar o cursor sem clear. Se persistir, experimente um terminal diferente.

---

📁 Estrutura do Projeto

```
webcam-to-ascii-art/
├── camera.py          # Código principal
├── README.md          # Este documento
└── requirements.txt   # (Opcional) opencv-python, numpy
```

---

🖼️ Exemplo de Código (Conversão de Cor)

```python
def frame_to_ascii_vectorized(frame, palette, new_width):
    # Redimensiona e extrai canais
    resized = cv2.resize(frame, (new_width, new_height))
    B, G, R = resized[..., 0], resized[..., 1], resized[..., 2]
    gray = (0.2989 * R + 0.5870 * G + 0.1140 * B).astype(np.uint8)
    indices = np.clip((gray / 255.0 * (len(palette) - 1)).astype(int), 0, len(palette)-1)
    char_array = np.array(list(palette))
    ascii_chars = char_array[indices]
    # Gera strings ANSI
    ...
```

---

🤝 Contribuição

Contribuições são muito bem-vindas! 🎉

· Sugira novas paletas de caracteres.
· Melhore a compatibilidade com diferentes terminais.
· Reporte bugs ou problemas de desempenho.
· Envie um pull request com suas alterações.

Veja as issues abertas para ideias do que pode ser feito.

---

📜 Licença

Este projeto está licenciado sob a licença MIT. Sinta-se livre para usar, modificar e compartilhar.

---

🙏 Agradecimentos

· Inspirado pelo site AsciiArt.eu - Webcam to ASCII Art e pela comunidade ASCII.
· Obrigado a todos que contribuíram com ideias e testes.

