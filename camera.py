#!/usr/bin/env python3
import cv2
import numpy as np
import sys
import os
import shutil
import time
import signal

# ----------------------------------------------------------------------
# Leitura de teclas não-bloqueante (cross-platform)
# ----------------------------------------------------------------------
if os.name == 'nt':
    import msvcrt
    def get_key_nonblock():
        if msvcrt.kbhit():
            key = msvcrt.getch()
            try: return key.decode('utf-8')
            except: return key.decode('latin-1', errors='replace')
        return None
else:
    import termios, select, tty
    def get_key_nonblock():
        fd = sys.stdin.fileno()
        try:
            old_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
            r, _, _ = select.select([sys.stdin], [], [], 0)
            return sys.stdin.read(1) if r else None
        except: return None
        finally: termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# ----------------------------------------------------------------------
# Paletas
# ----------------------------------------------------------------------
PALETTES = {
    "1. Single block": "█",
    "2. Solid block": "▓▒░ ",
    "3. Minimalist": ". ",
    "4. Medium set": "@%#*+=-:. ",
    "5. Longer set": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "6. Binary": "01",
    "7. Braille": "⠀⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟",
    "8. Extended Braille": "⠀⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠩⠚⠛⠜⠩⠝⠩⠩⠩",
    "9. Shades": " ░▒▓█",
    "10. Crosshatch": " .:/\\|X#",
    "11. Math": " .+=÷×∞",
    "12. Arrows": " .·+*#%@►◄▲▼",
    "13. Blocks": " ▖▗▘▙▚▛▜▟█",
    "14. Dots": " .·°º¤",
    "15. Matrix": " 01",
    "16. Geometric": " .•○●",
    "17. Slash": " \\|/",
    "18. Vertical": "  ▂▃▄▅▆▇█",
    "19. Brackets": " ([{}])",
    "20. Currency": " .:-¡¢£¤¥¦§¨©ª",
    "21. Alpha": "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
}

# ----------------------------------------------------------------------
def get_terminal_size_full():
    """Captura o tamanho exato do terminal."""
    try:
        cols, lines = shutil.get_terminal_size()
        return cols, lines
    except:
        return 80, 24

# ----------------------------------------------------------------------
def show_menu():
    """Exibe o menu e retorna o nome da paleta escolhida."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print(" SELECIONE A PALETA ".center(60, "="))
    print("=" * 60)
    keys = list(PALETTES.keys())
    for name in keys:
        print(f"  {name}")
    print("\n  Q. Sair")
    print("-" * 60)
    
    while True:
        choice = input("Digite o número (ou Q): ").strip().lower()
        if choice == 'q': sys.exit(0)
        for name in keys:
            if name.startswith(choice + '.'): return name
        print("Opção inválida.")

# ----------------------------------------------------------------------
# Funções vetorizadas para geração da arte ASCII
# ----------------------------------------------------------------------
def frame_to_ascii_vectorized(frame, palette, tw, th):
    """
    Converte um frame BGR para uma string ASCII colorida usando NumPy.
    Retorna a string pronta para exibição preenchendo todo o terminal.
    """
    resized = cv2.resize(frame, (tw, th)) # Redimensiona para ocupar 100% do terminal
    
    B, G, R = resized[..., 0], resized[..., 1], resized[..., 2] # Separa canais BGR e converte para RGB
    gray = (0.2989 * R + 0.5870 * G + 0.1140 * B).astype(np.uint8) # Calcula luminância (escala de cinza)

    indices = (gray / 255.0 * (len(palette) - 1)).astype(int) # Mapeia intensidade para índices da paleta
    np.clip(indices, 0, len(palette) - 1, out=indices)
    
    char_array = np.array(list(palette)) # Array de caracteres da paleta
    ascii_chars = char_array[indices]

    def make_ansi(r, g, b, ch):
        return f"\033[38;2;{r};{g};{b}m{ch}"
    
    vfunc = np.frompyfunc(make_ansi, 4, 1) # Função vetorizada para criar string ANSI colorida por pixel
    ansi_matrix = vfunc(R, G, B, ascii_chars)

    lines_out = [''.join(row) + "\033[0m\033[K" for row in ansi_matrix] # Junta as linhas com reset e limpeza de resíduos
    return '\n'.join(lines_out) + "\033[J"

# ----------------------------------------------------------------------
def main():
    while True:
        palette_name = show_menu()
        active_palette = PALETTES[palette_name]

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Erro ao acessar câmera.")
            return

        # Sequências ANSI de controle
        ENTER_ALT, EXIT_ALT = "\033[?1049h", "\033[?1049l"
        HIDE_CUR, SHOW_CUR = "\033[?25l", "\033[?25h"
        HOME = "\033[H"

        sys.stdout.write(ENTER_ALT + HIDE_CUR)
        sys.stdout.flush()

        running = [True] 
        def cleanup(return_to_menu=True):
            if running[0]:
                running[0] = False
                cap.release()
                sys.stdout.write("\033[0m" + SHOW_CUR + EXIT_ALT)
                sys.stdout.flush()
            if not return_to_menu:
                sys.exit(0)

        signal.signal(signal.SIGINT, lambda s, f: cleanup(return_to_menu=True))

        try:
            while running[0]:
                start_time = time.time()
                ret, frame = cap.read()
                if not ret: break

                tw, th = get_terminal_size_full() # Atualiza tamanho da janela a cada frame
                
                ascii_art = frame_to_ascii_vectorized(frame, active_palette, tw, th)

                sys.stdout.write(HOME + ascii_art) # Posiciona cursor no início e imprime
                sys.stdout.flush()

                key = get_key_nonblock() # Verifica teclas
                if key == 'q':
                    cleanup(return_to_menu=False)
                    return
                elif key == 'p':
                    names = list(PALETTES.keys())
                    idx = (names.index(palette_name) + 1) % len(names)
                    palette_name = names[idx]
                    active_palette = PALETTES[palette_name]

                elapsed = time.time() - start_time # Controle de FPS
                if (1/30) > elapsed: time.sleep((1/30) - elapsed)

        except (KeyboardInterrupt, EOFError):
            cleanup(return_to_menu=True)
        finally:
            cap.release()
            sys.stdout.write("\033[0m" + SHOW_CUR + EXIT_ALT)
            sys.stdout.flush()

if __name__ == "__main__":
    main()