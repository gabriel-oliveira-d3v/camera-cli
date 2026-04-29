
# ----------------------------------------------------------------------
# Leitura de teclas não-bloqueante (cross-platform)
# ----------------------------------------------------------------------
if os.name == 'nt':
    import msvcrt
    def get_key_nonblock():
        if msvcrt.kbhit():
            key = msvcrt.getch()
            try:
                return key.decode('utf-8')
            except UnicodeDecodeError:
                return key.decode('latin-1', errors='replace')
        return None
else:
    import termios
    import select
    import tty

    def get_key_nonblock():
        fd = sys.stdin.fileno()
        try:
            old_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
            r, _, _ = select.select([sys.stdin], [], [], 0)
            if r:
                return sys.stdin.read(1)
            return None
        except:
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# ----------------------------------------------------------------------
# Paletas
# ----------------------------------------------------------------------
PALETTES = {
    "1. Single block":   "█",
    "2. Solid block":    "▓▒░ ",
    "3. Minimalist":     ". ",
    "4. Medium set":     "@%#*+=-:. ",
    "5. Longer set":     "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "6. Full set":       "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "7. Max":            " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "8. Alphabetic":     "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ",
    "9. Alphanumeric":   "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ",
    "10. Arrow":         " .-+*#%@►◄▲▼",
    "11. Extended High": "█▓▒░@#%&*+-=:. ",
    "12. Math Symbols":  "∑∫√∞≈≠≤≥÷×¬∧∨∩∪∈∉⊂⊃⊆⊇⊕⊗⊥∠∟∆∇∂∈∋∀∃∄∅∗∘∙√∛∜∝∞∟∠∡∢ ",
    "13. Numerical":     "0O8@%#*+=-:,. ",
    "14. Binary":        "01",
}

# ----------------------------------------------------------------------
def get_terminal_width(offset=4, fallback=160):
    try:
        cols, _ = shutil.get_terminal_size()
        return max(20, cols - offset)
    except:
        return fallback

# ----------------------------------------------------------------------
def show_menu():
    """Exibe o menu e retorna o nome da paleta escolhida."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print(" Webcam → ASCII Art Colorida ".center(60, "="))
    print("=" * 60)
    print("\nEscolha uma paleta de caracteres:\n")
    for name in PALETTES.keys():
        print(f"  {name}")
    print("\n  Q. Sair")
    print("-" * 60)
    
    while True:
        choice = input("Digite o número (ou Q): ").strip().lower()
        if choice == 'q':
            sys.exit(0)
        for name in PALETTES.keys():
            if name.startswith(choice + '.'):
                return name
        print("Opção inválida. Tente novamente.")

# ----------------------------------------------------------------------
# Funções vetorizadas para geração da arte ASCII
# ----------------------------------------------------------------------
def frame_to_ascii_vectorized(frame, palette, new_width):
    """
    Converte um frame BGR para uma string ASCII colorida usando NumPy.
    Retorna a string pronta para exibição.
    """
    # Redimensiona mantendo proporção
    height, width = frame.shape[:2]
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)
    resized = cv2.resize(frame, (new_width, new_height))

    # Separa canais BGR e converte para RGB
    B, G, R = resized[..., 0], resized[..., 1], resized[..., 2]

    # Calcula luminância (escala de cinza)
    gray = (0.2989 * R + 0.5870 * G + 0.1140 * B).astype(np.uint8)

    # Mapeia intensidade para índices da paleta
    indices = (gray / 255.0 * (len(palette) - 1)).astype(int)
    np.clip(indices, 0, len(palette) - 1, out=indices)

    # Array de caracteres da paleta
    char_array = np.array(list(palette))
    ascii_chars = char_array[indices]   # matriz (new_height, new_width) de caracteres

    # Função vetorizada para criar string ANSI colorida por pixel
    def make_ansi(r, g, b, ch):
        return f"\033[38;2;{r};{g};{b}m{ch}"
    vfunc = np.frompyfunc(make_ansi, 4, 1)
    ansi_matrix = vfunc(R, G, B, ascii_chars)  # array de objetos string

    # Junta as linhas com reset de cor e quebra de linha
    lines = []
    for row in ansi_matrix:
        line = ''.join(row)
        # Garante largura exata preenchendo com espaços se necessário
        if len(line) < new_width:
            line += ' ' * (new_width - len(line))
        lines.append(line + "\033[0m")
    return '\n'.join(lines)

# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Webcam ASCII Art Colorida (otimizada)")
    parser.add_argument("--offset", type=int, default=4,
                        help="Colunas a subtrair da largura do terminal (padrão: 4)")
    args = parser.parse_args()
    offset = args.offset

    # Menu inicial
    palette_name = show_menu()
    active_palette = PALETTES[palette_name]

    # Câmera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: não foi possível acessar a webcam.")
        sys.exit(1)

    ascii_width = get_terminal_width(offset)
    frame_count = 0
    last_check = 0

    print(f"\nIniciando com paleta: {palette_name}")
    print("Largura ajustada:", ascii_width, "colunas")
    print("Controles: 'p' troca paleta, 'q' sai, 'h' ajuda")
    time.sleep(1.5)

    # FPS alvo
    target_fps = 30
    frame_time = 1.0 / target_fps

    # Move cursor para o topo (modo de sobreposição)
    HOME_CURSOR = "\033[H"

    try:
        while True:
            start_time = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            # Atualiza largura a cada 30 quadros
            frame_count += 1
            if frame_count - last_check >= 30:
                new_width = get_terminal_width(offset)
                if new_width != ascii_width:
                    ascii_width = new_width
                last_check = frame_count

            # Gera arte ASCII vetorizada
            ascii_art = frame_to_ascii_vectorized(frame, active_palette, ascii_width)

            # Posiciona cursor no início e imprime
            sys.stdout.write(HOME_CURSOR + ascii_art)
            sys.stdout.write(f"\nPaleta: {palette_name.split('.',1)[1].strip()} | {ascii_width} col. | 'p' troca 'q' sai 'h' ajuda")
            sys.stdout.flush()

            # Verifica teclas
            key = get_key_nonblock()
            if key is not None:
                key = key.lower()
                if key == 'q':
                    break
                elif key == 'p':
                    names = list(PALETTES.keys())
                    idx = names.index(palette_name)
                    idx = (idx + 1) % len(names)
                    palette_name = names[idx]
                    active_palette = PALETTES[palette_name]
                elif key == 'h':
                    sys.stderr.write("\n[p]aleta seguinte  [q]sair  [h]ajuda\n")

            # Controle de FPS
            elapsed = time.time() - start_time
            sleep_time = frame_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        sys.stdout.write("\033[0m\033[H\033[2J")   # reset de cor + limpa tela
        print("Programa encerrado.")

if __name__ == "__main__":
    main()
