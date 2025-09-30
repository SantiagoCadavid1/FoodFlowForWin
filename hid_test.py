import keyboard

def main():
    print("=== HID Tester (modo teclado emulado) ===")
    print("Pasa una tarjeta por el lector...")
    print("Presiona CTRL+C para salir.\n")

    buffer = ""

    try:
        while True:
            event = keyboard.read_event(suppress=False)  # leer cada evento
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == "enter":
                    if buffer:
                        print(f"Tarjeta leída: {buffer}")
                        buffer = ""
                elif len(event.name) == 1:  # solo caracteres normales
                    buffer += event.name
                else:
                    # Ignorar teclas especiales como shift, ctrl, etc.
                    pass
    except KeyboardInterrupt:
        print("\nSaliendo del HID Tester...")

if __name__ == "__main__":
    main()

