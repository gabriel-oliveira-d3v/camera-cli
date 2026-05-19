#!/usr/bin/env python3
import cv2
import numpy as np
import sys
import os
import shutil
import time
import argparse
from collections import deque


# ----------------------------------------------------------------------
# Leitura de teclas nao-bloqueante (cross-platform)
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

    def set_raw_input(fd):
        mode = termios.tcgetattr(fd)
        mode[tty.IFLAG] &= ~(tty.BRKINT | tty.ICRNL | tty.INPCK | tty.ISTRIP | tty.IXON)
        mode[tty.OFLAG] |= tty.OPOST
        mode[tty.CFLAG] &= ~(tty.CSIZE | tty.PARENB)
        mode[tty.CFLAG] |= tty.CS8
        mode[tty.LFLAG] &= ~(tty.ECHO | tty.ICANON | tty.IEXTEN | tty.ISIG)
        mode[tty.CC][tty.VMIN] = 1
        mode[tty.CC][tty.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSADRAIN, mode)

    def read_key_nonblock(fd):
        r, _, _ = select.select([fd], [], [], 0)
        if r:
            return os.read(fd, 1).decode('utf-8', errors='replace')
        return None

# ----------------------------------------------------------------------
# Paletas
# ----------------------------------------------------------------------
PALETTES = {
    "1. Single block": "\u2588",
    "2. Solid block": "\u2593\u2592\u2591 ",
    "3. Minimalist": ". ",
    "4. Medium set": "@%#*+=-:. ",
    "5. Longer set": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "8. Braille": "\u2800\u2801\u2802\u2803\u2804\u2805\u2806\u2807\u2808\u2809\u280a\u280b\u280c\u280d\u280e\u280f\u2810\u2811\u2812\u2813\u2814\u2815\u2816\u2817\u2818\u2819\u281a\u281b\u281c\u281d\u281e\u281f\u2820\u2821\u2822\u2823\u2824\u2825\u2826\u2827",
    "9. Extended Braille": "\u2800\u2840\u2804\u2842\u2820\u2824\u2846\u2842\u2810\u2822\u2814\u2832\u2850\u2830\u2860\u2870\u2880\u2884\u2886\u2882\u2890\u2898\u289a\u289b\u289f\u28bf",
    "10. Shades": " \u2591\u2592\u2593\u2588",
    "11. Crosshatch": " .:/\\|X#",
    "12. Math": " .+=\xf7\xd7\u221e",
    "13. Arrows": " .\xb7+*#%@\u25ba\u25c4\u25b2\u25bc",
    "14. Blocks": " \u2596\u2597\u2598\u2599\u259a\u259b\u259c\u259d\u259e\u2588",
    "15. Dots": " .\xb7\xba\xa4",
    "16. Matrix": "0101",
    "17. Geometric": " .\u2022\u25cb\u25cf",
    "18. Slash": " \\|/",
    "19. Vertical": "  \u2582\u2583\u2584\u2585\u2586\u2587\u2588",
    "20. Brackets": " ([{}])",
    "21. Currency": " .:-\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa",
    "22. Alpha": "ABCDEFGHIJKLMNOPQRSTUVWXYZ ",
    "23. Halftone dots": " \xb7\u25cb\u25d4\u25d0\u25d5\u25cf",
    "24. Pixel shades": " \u258f\u258e\u258d\u258c\u258b\u258a\u2589\u2588",
    "25. Crosshatch fine": " .:!/\\|(){}[]#%#",
    "26. Waves & lines": " \xb7~=-_`'\xb4\xaf",
    "27. Stipple classic": " .:-=+*#%@",
    "28. Block progression": " \u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588",
    "29. Braille dots 1": " \u2801\u2802\u2804\u2840\u2820\u2820\u2810\u2808",
    "30. Box drawing light": " \u2500\u2502\u250c\u2510\u2514\u2518\u251c\u2524\u252c\u2534\u253c",
    "31. Runes minimal": " \xb7\u1680\u1681\u1682\u1683\u1684\u1685\u1686\u1687",
    "32. Hatching slashes": " \xb7/|\\\\//\\\\/X",
    "33. Geometric shapes": " \u25a1\u25f1\u25e7\u25e8\u25e9\u25ea\u25eb\u25f0\u25f2\u25f3\u25f4\u25f5\u25f6\u25f7\u269a",
    "34. Musical density": " \u2669\u266a\u266b\u266c",
    "35. Math symbols": " \u2212\xb1\xd7\xf7\u221e\u2248\u2260\u2261\u2264\u2265"
}

PALETTE_NAMES = list(PALETTES.keys())

# ----------------------------------------------------------------------
# Constantes
# ----------------------------------------------------------------------
DEFAULT_FPS = 30
HELP_LINES = 6

# ----------------------------------------------------------------------
def get_terminal_size_full():
    try:
        cols, lines = shutil.get_terminal_size()
        return cols, lines
    except:
        return 80, 24

# ----------------------------------------------------------------------
def palette_preview(palette, max_chars=10):
    s = palette[:max_chars].replace(' ', '\xb7')
    return s

# ----------------------------------------------------------------------
def show_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print(" SELECIONE A PALETA ".center(60, "="))
    print("=" * 60)
    for name in PALETTE_NAMES:
        preview = palette_preview(PALETTES[name])
        print(f"  {name:<30s} [{preview}]")
    print("\n  Q. Sair")
    print("-" * 60)

    while True:
        choice = input("Digite o numero (ou Q): ").strip().lower()
        if choice == 'q':
            sys.exit(0)
        for name in PALETTE_NAMES:
            if name.startswith(choice + '.'):
                return name
        print("Opcao invalida.")

# ----------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Camera ASCII art terminal viewer")
    parser.add_argument("-c", "--camera", type=int, default=0, help="Camera device index")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help="Target FPS")
    parser.add_argument("--scale", type=float, default=1.0, help="Scale factor (0.1-3.0)")
    parser.add_argument("--no-color", action="store_true", help="Monochrome mode")
    parser.add_argument("--invert", action="store_true", help="Invert colors")
    parser.add_argument("--brightness", type=int, default=0, help="Brightness (-127 a 127)")
    parser.add_argument("--contrast", type=int, default=0, help="Contrast (-127 a 127)")
    parser.add_argument("--edge", action="store_true", help="Edge detection mode")
    parser.add_argument("--flip", action="store_true", help="Flip horizontalmente")
    parser.add_argument("--zoom", type=float, default=1.0, help="Zoom digital (1.0-10.0)")
    return parser.parse_args()

# ----------------------------------------------------------------------
def process_frame(frame, state):
    if state.flip:
        frame = cv2.flip(frame, 1)
    if state.brightness != 0 or state.contrast != 0:
        alpha = 1.0 + state.contrast / 127.0
        beta = state.brightness
        frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
    if state.edge:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    if state.zoom != 1.0:
        fh, fw = frame.shape[:2]
        cw = int(fw / state.zoom)
        ch = int(fh / state.zoom)
        x1 = max(0, (fw - cw) // 2)
        y1 = max(0, (fh - ch) // 2)
        frame = frame[y1:y1+ch, x1:x1+cw]
    return frame

# ----------------------------------------------------------------------
def frame_to_ascii(resized, palette, use_color):
    B, G, R = resized[..., 0], resized[..., 1], resized[..., 2]
    gray = (0.2989 * R + 0.5870 * G + 0.1140 * B).astype(np.uint8)

    indices = (gray / 255.0 * (len(palette) - 1)).astype(int)
    np.clip(indices, 0, len(palette) - 1, out=indices)

    char_array = np.array(list(palette))
    ascii_chars = char_array[indices]

    if use_color:
        vfunc = np.frompyfunc(
            lambda r, g, b, ch: f"\033[38;2;{r};{g};{b}m{ch}", 4, 1
        )
        ansi_matrix = vfunc(R, G, B, ascii_chars)
        lines = [''.join(row) + "\033[0m\033[K" for row in ansi_matrix]
    else:
        lines = [''.join(row) + "\033[0m\033[K" for row in ascii_chars]

    return '\n'.join(lines) + "\033[J"

# ----------------------------------------------------------------------
def frame_to_ascii_plain(resized, palette):
    B, G, R = resized[..., 0], resized[..., 1], resized[..., 2]
    gray = (0.2989 * R + 0.5870 * G + 0.1140 * B).astype(np.uint8)
    indices = (gray / 255.0 * (len(palette) - 1)).astype(int)
    np.clip(indices, 0, len(palette) - 1, out=indices)
    char_array = np.array(list(palette))
    ascii_chars = char_array[indices]
    return '\n'.join(''.join(row) for row in ascii_chars)

# ----------------------------------------------------------------------
def build_help_text(width):
    sep = "\033[2m" + "\u2500" * width + "\033[0m"
    kw = "\033[33m"
    nf = "\033[0m"
    return "\n".join([
        sep,
        f" {kw}q{nf} -> sair  {kw}p{nf} -> paleta  {kw}f{nf} -> flip  {kw}i{nf} -> inverter  {kw}c{nf} -> cor",
        f" {kw}e{nf} -> edge  {kw}h{nf} -> ajuda  {kw}={nf} -> escala  {kw}-{nf} -> escala  {kw}z{nf}/{kw}Z{nf} -> zoom",
        f" {kw}b{nf}/{kw}B{nf} -> brilho  {kw}[{nf}/{kw}]{nf} -> contraste",
        sep,
    ])

# ----------------------------------------------------------------------
def build_status_line(state, fps, tw):
    pal_short = state.palette_name[:18]
    parts = [
        f"FPS:{fps:5.1f}",
        f"Pal:{pal_short}",
        "COLOR" if state.color else "MONO",
    ]
    if state.edge: parts.append("EDGE")
    if state.invert: parts.append("INV")
    if state.flip: parts.append("FLIP")

    text = "  ".join(parts)
    text = text[:tw]
    return f"\033[30;47m{text:<{tw}}\033[0m\033[K"

# ----------------------------------------------------------------------
def handle_key(key, state):
    if key is None: return
    if key == 'p':
        idx = PALETTE_NAMES.index(state.palette_name)
        state.palette_name = PALETTE_NAMES[(idx + 1) % len(PALETTE_NAMES)]
        state.palette = PALETTES[state.palette_name]
        return
    if key == 'f': state.flip = not state.flip; return
    if key == 'i': state.invert = not state.invert; return
    if key == 'c': state.color = not state.color; return
    if key == 'e': state.edge = not state.edge; return
    if key == 'h': state.help_until = time.time() + 4; return
    if key in ('=', '+'): state.scale = min(3.0, state.scale * 1.25); return
    if key == '-': state.scale = max(0.1, state.scale / 1.25); return
    if key == 'z': state.zoom = min(10.0, state.zoom * 1.5); return
    if key == 'Z': state.zoom = max(1.0, state.zoom / 1.5); return
    if key == 'b': state.brightness = max(-127, state.brightness - 10); return
    if key == 'B': state.brightness = min(127, state.brightness + 10); return
    if key == '[': state.contrast = max(-127, state.contrast - 10); return
    if key == ']': state.contrast = min(127, state.contrast + 10); return

# ----------------------------------------------------------------------
class State:
    def __init__(self, args, palette_name):
        self.palette_name = palette_name
        self.palette = PALETTES[palette_name]
        self.color = not args.no_color
        self.invert = args.invert
        self.flip = args.flip
        self.edge = args.edge
        self.brightness = args.brightness
        self.contrast = args.contrast
        self.scale = args.scale
        self.zoom = args.zoom
        self.target_fps = args.fps
        self.camera_idx = args.camera
        self.help_until = 0

# ----------------------------------------------------------------------
def main():
    args = parse_args()

    ENTER_ALT, EXIT_ALT = "\033[?1049h", "\033[?1049l"
    HIDE_CUR, SHOW_CUR = "\033[?25l", "\033[?25h"
    HOME = "\033[H"

    cap = None

    try:
        while True:
            palette_name = show_menu()
            state = State(args, palette_name)

            cap = cv2.VideoCapture(state.camera_idx)
            if not cap.isOpened():
                print("Erro ao acessar camera.")
                return

            sys.stdout.write(ENTER_ALT + HIDE_CUR)
            sys.stdout.flush()

            # Ativa raw mode continuo (Unix) - teclas nunca sao perdidas
            raw_fd = -1
            old_term = None
            if os.name != 'nt':
                try:
                    raw_fd = sys.stdin.fileno()
                    old_term = termios.tcgetattr(raw_fd)
                    set_raw_input(raw_fd)
                except:
                    raw_fd = -1

            frame_times = deque(maxlen=30)
            fps = 0.0

            try:
                while True:
                    loop_start = time.time()

                    ret, frame = cap.read()
                    if not ret:
                        break

                    frame = process_frame(frame, state)

                    if state.invert:
                        frame = cv2.bitwise_not(frame)

                    tw, th = get_terminal_size_full()
                    show_help = time.time() < state.help_until
                    reserved = 1 + (HELP_LINES if show_help else 0)

                    dw = max(1, int(tw * state.scale))
                    dh = max(1, min(th, int(th * state.scale)) - reserved)

                    resized = cv2.resize(frame, (dw, dh))
                    ascii_art = frame_to_ascii(resized, state.palette, state.color)

                    output = ascii_art

                    if show_help:
                        help_text = build_help_text(tw)
                        output += "\n" + help_text + "\n"

                    status_line = build_status_line(state, fps, tw)
                    output += "\n" + status_line + "\033[J"

                    sys.stdout.write(HOME + output)
                    sys.stdout.flush()

                    # Leitura de tecla (raw mode continuo no Unix)
                    key = None
                    if raw_fd >= 0:
                        key = read_key_nonblock(raw_fd)
                        if key == '\x03':
                            raise KeyboardInterrupt
                    elif os.name == 'nt':
                        key = get_key_nonblock()

                    if key == 'q':
                        return
                    else:
                        handle_key(key, state)

                    now = time.time()
                    frame_times.append(now - loop_start)
                    if len(frame_times) >= 2:
                        total = sum(frame_times)
                        fps = len(frame_times) / total if total > 0 else 0

                    elapsed = time.time() - loop_start
                    target_dt = 1.0 / state.target_fps
                    if elapsed < target_dt:
                        time.sleep(target_dt - elapsed)

            except (KeyboardInterrupt, EOFError):
                pass
            finally:
                if raw_fd >= 0:
                    try:
                        termios.tcsetattr(raw_fd, termios.TCSADRAIN, old_term)
                    except:
                        pass
                if cap is not None:
                    cap.release()
                    cap = None
                sys.stdout.write("\033[0m" + SHOW_CUR + EXIT_ALT)
                sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        if cap is not None:
            cap.release()
        sys.stdout.write("\033[0m" + SHOW_CUR)
        sys.stdout.flush()

if __name__ == "__main__":
    main()
