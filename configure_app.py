import json
import os
import pywinusb.hid as hid  # <- Import correcto

CONFIG_FILE = "config.json"

def listar_dispositivos():
    all_devices = hid.HidDeviceFilter().get_devices()
    if not all_devices:
        print("No se encontraron dispositivos HID.")
        return []

    print("\n=== Dispositivos HID detectados ===")
    for i, d in enumerate(all_devices):
        print(f"[{i}] VID: 0x{d.vendor_id:04x}, PID: 0x{d.product_id:04x}, Producto: {d.product_name}")
    return all_devices

def main():
    print("=== Configuración de FoodFlow ===")

    # Solicitar parámetros al usuario
    sede = input("Ingrese la sede: ").strip()

    # Listar dispositivos HID
    dispositivos = listar_dispositivos()
    if not dispositivos:
        print("No se pudo configurar el lector RFID porque no hay dispositivos HID.")
        return

    try:
        seleccion = int(input("\nSeleccione el número del lector RFID: "))
        if seleccion < 0 or seleccion >= len(dispositivos):
            print("Selección inválida.")
            return

        dispositivo = dispositivos[seleccion]

        lector_rfid = {
            "vid": f"0x{dispositivo.vendor_id:04x}",
            "pid": f"0x{dispositivo.product_id:04x}",
            "producto": dispositivo.product_name
        }

        # Crear diccionario de configuración
        config = {
            "sede": sede,
            "lector_rfid": lector_rfid
        }

        # Guardar en archivo JSON
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        print(f"\nConfiguración guardada en {os.path.abspath(CONFIG_FILE)}")
        print(json.dumps(config, indent=4, ensure_ascii=False))

    except ValueError:
        print("Entrada inválida.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error inesperado:", e)
    finally:
        input("\nPresiona ENTER para salir...")
