import hid

def listar_dispositivos():
    dispositivos = hid.enumerate()
    if not dispositivos:
        print("No se encontraron dispositivos HID.")
        return []

    print("=== Dispositivos HID detectados ===")
    for i, d in enumerate(dispositivos):
        print(f"[{i}] VID: {d['vendor_id']:04x}, PID: {d['product_id']:04x}, "
              f"Product: {d.get('product_string', '')}, "
              f"Manufacturer: {d.get('manufacturer_string', '')}")
    return dispositivos

def probar_dispositivo(device_info):
    try:
        device = hid.Device(device_info['vendor_id'], device_info['product_id'])
        print(f"\nConectado a: {device_info.get('product_string', 'Desconocido')}")
        print("Leyendo datos... (Ctrl+C para salir)\n")

        while True:
            data = device.read(64)  # Lee hasta 64 bytes
            if data:
                print("Datos crudos:", data)
                try:
                    texto = "".join(chr(b) for b in data if b > 0x1F and b < 0x7F)
                    if texto:
                        print("Texto decodificado:", texto)
                except:
                    pass

    except Exception as e:
        print("Error al abrir el dispositivo:", e)

def main():
    dispositivos = listar_dispositivos()
    if not dispositivos:
        return

    try:
        seleccion = int(input("\nSelecciona el número del dispositivo a probar: "))
        if seleccion < 0 or seleccion >= len(dispositivos):
            print("Selección inválida.")
            return
        probar_dispositivo(dispositivos[seleccion])
    except ValueError:
        print("Entrada inválida.")

if __name__ == "__main__":
    main()
