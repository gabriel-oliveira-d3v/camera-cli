import cv2
import numpy as np
import sys
import time
import os

# Mapeamento de intensidade -> caracteres (do mais escuro ao mais claro)
ASCII_CHARS = "@%#*+=-:. "

def pixel_to_ascii(pixel_value):
    """Converte um valor de pixel (0-255) para um caractere ASCII."""
    index = int(pixel_value / 255 * (len(ASCII_CHARS) - 1))
    return ASCII_CHARS[index]

def frame_to_ascii(frame, new_width=80):
    """Converte um frame em tons de cinza para arte ASCII."""
    # Converte para cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Calcula nova altura mantendo a proporção (caracteres são mais altos que largos)
    height, width = gray.shape
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)  # 0.55 corrige proporção do terminal
    resized = cv2.resize(gray, (new_width, new_height))
    
    # Converte cada pixel para caractere
    ascii_frame = ""
    for row in resized:
        for pixel in row:
            ascii_frame += pixel_to_ascii(pixel)
        ascii_frame += "\n"
    
    return ascii_frame

def clear_screen():
    """Limpa o terminal (funciona no Windows/Linux/Mac)."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    cap = cv2.VideoCapture(0)  # 0 = webcam padrão
    if not cap.isOpened():
        print("Erro: não foi possível acessar a webcam.")
        return
    
    print("Pressione Ctrl+C no terminal para sair.")
    time.sleep(1)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            ascii_art = frame_to_ascii(frame, new_width=100)  # Ajuste a largura
            clear_screen()
            sys.stdout.write(ascii_art)
            sys.stdout.flush()
            
            # Pequeno delay para não sobrecarregar a CPU
            time.sleep(0.05)
            
            # Opcional: sair ao pressionar 'q' na janela da webcam
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\nEncerrado.")

if __name__ == "__main__":
    main()
