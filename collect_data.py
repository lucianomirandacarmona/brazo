import csv
import time
import serial

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
CSV_FILE = "dataset_ecg.csv"

LABELS = {
    "1": "relajado",
    "2": "extendido",
    "3": "contraido",
}


def clear_serial_buffer(ser):
    """Borra datos pendientes del puerto serie."""
    try:
        ser.reset_input_buffer()
    except Exception:
        pass

    try:
        ser.reset_output_buffer()
    except Exception:
        pass

    time.sleep(0.2)


def parse_line(raw_line: bytes):
    """
    Espera una línea tipo: 'maximo,minimo,valor'
    Ejemplo: '1023,22,843'
    """
    text = raw_line.decode("utf-8", errors="ignore").strip()
    if not text:
        return None

    # limpia espacios y separadores extra
    text = text.replace(";", ",").replace(" ", "")
    parts = text.split(",")

    if len(parts) < 3:
        return None

    try:
        maximo = float(parts[0])
        minimo = float(parts[1])
        valor = float(parts[2])
        return maximo, minimo, valor
    except ValueError:
        return None


def collect_samples_for_label(ser, label, samples_to_collect):
    print(f"\nManten la mano en: {label}")
    print(f"Voy a guardar {samples_to_collect} muestras...")
    clear_serial_buffer(ser)
    count = 0

    while count < samples_to_collect:
        raw = ser.readline()
        if not raw:
            continue

        parsed = parse_line(raw)
        if parsed is None:
            continue

        maximo, minimo, valor = parsed

        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([label, maximo, minimo, valor])

        count += 1
        if count % 10 == 0:
            print(f"  {count}/{samples_to_collect} muestras guardadas")

    print(f"Listo: {label} guardado.")


def main():
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        time.sleep(2)
        clear_serial_buffer(ser)
        print(f"Conectado a {PORT} ({BAUDRATE})")
    except Exception as e:
        print(f"No pude abrir {PORT}: {e}")
        print("Revisa que el ESP32 esté conectado y que el puerto sea correcto.")
        print("También puedes probar: ls /dev/ttyUSB*")
        return

    # si el archivo no existe, lo creamos con encabezado
    try:
        with open(CSV_FILE, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["label", "maximo", "minimo", "valor"])
    except FileExistsError:
        pass

    print("Instrucciones:")
    print("  1 = relajado")
    print("  2 = extendido")
    print("  3 = contraido")
    print("  q = salir")
    print()

    while True:
        opcion = input("Selecciona la clase a capturar: ").strip().lower()

        if opcion == "q":
            print("Saliendo...")
            ser.close()
            break

        if opcion not in LABELS:
            print("Opción inválida. Usa 1, 2, 3 o q.")
            continue

        label = LABELS[opcion]

        try:
            n = int(input("Cuántas muestras quieres guardar para esta clase? "))
        except ValueError:
            print("Debes ingresar un número entero.")
            continue

        if n <= 0:
            print("Debe ser mayor que 0.")
            continue

        collect_samples_for_label(ser, label, n)

        print("\nSiguiente clase...")
        print("  1 = relajado")
        print("  2 = extendido")
        print("  3 = contraido")
        print("  q = salir")


if __name__ == "__main__":
    main()