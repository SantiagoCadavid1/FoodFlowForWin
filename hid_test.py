import pywinusb.hid as hid
import time

def listar_dispositivos():
    dispositivos = hid.HidDeviceFilter().get_devices()
    if not dispositivos:
        print("No se encontraron dispositivos HID.")
        return []
    print("=== Dispositivos HID detectados ===")
    for i, d in enumerate(dispositivos):
        print(f"[{i}] VID: {hex(d.vendor_id)}, PID: {hex(d.product_id)}, "
              f"Producto: {d.product_name}")
    return dispositivos

def raw_handler(data):
    # data[0] es el report_id, los datos reales empiezan en data[1:]
    print("Datos crudos:", data)

    # Intentar decodificar como texto legible
    texto = "".join(chr(b) for b in data[1:] if 32 <= b < 127)
    if texto:
        print("Texto decodificado:", texto)

def probar_dispositivo(device):
    try:
        device.open()
        device.set_raw_data_handler(raw_handler)
        print(f"\nConectado a: {device.product_name}")
        print("Leyendo datos... (Ctrl+C para salir)\n")

        while True:
            time.sleep(0.5)
    except Exception as e:
        print("Error al abrir el dispositivo:", e)
    finally:
        try:
            device.close()
        except:
            pass

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
    try:
        main()
    except Exception as e:
        print("Error inesperado:", e)
    finally:
        input("\nPresiona ENTER para salir...")
