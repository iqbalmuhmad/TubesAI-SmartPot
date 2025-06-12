import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import serial
import time

# --- 1. Load Dataset ---
try:
    df = pd.read_csv(r'C:\AI\dataset_suhu_kelembaban.csv')
    print("✅ Dataset berhasil dimuat.")
except FileNotFoundError:
    print("❌ File dataset_suhu_kelembaban.csv tidak ditemukan.")
    exit()

X = df[['Suhu (°C)', 'Kelembaban (%)']]
y = df['Output (1=ON, 0=OFF)']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- 2. Latih Model Decision Tree ---
model = DecisionTreeClassifier(criterion='entropy', max_depth=4, random_state=0)
model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"🎯 Akurasi Decision Tree: {accuracy * 100:.2f}%\n")

# --- 3. Koneksi ke Arduino ---
arduino_port = 'COM7'  # Ganti dengan port Anda
baud_rate = 115200

try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"🔌 Terhubung ke Arduino di {arduino_port}")
    time.sleep(2)
except serial.SerialException as e:
    print(f"❌ Gagal koneksi ke Arduino: {e}")
    exit()

print("▶️ Membaca data dari Arduino...\n")

# --- 4. Loop Prediksi AI dan Komunikasi Serial ---
try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if not line or "LED" in line:
                continue

            print(f"[DEBUG] Baris mentah dari Arduino: {repr(line)}")

            parts = line.split(',')
            if len(parts) != 3:
                print(f"⚠️ Format data salah: {line}")
                continue

            try:
                # Strip whitespace dari masing-masing bagian dan ubah ke float
                suhu = float(parts[0].strip())
                kelembaban_udara = float(parts[1].strip())
                kelembaban_tanah = float(parts[2].strip())

                # Buat data untuk model prediksi
                input_data = pd.DataFrame([[suhu, kelembaban_udara]], columns=['Suhu (°C)', 'Kelembaban (%)'])
                prediction = model.predict(input_data)[0]

                # Kirim hasil ke Arduino dan tampilkan semua data
                if prediction == 1:
                    ser.write(b'1\n')
                    print(f"🌡️ Suhu={suhu}, RH={kelembaban_udara}, Tanah={kelembaban_tanah} → LED ON")
                else:
                    ser.write(b'0\n')
                    print(f"🌡️ Suhu={suhu}, RH={kelembaban_udara}, Tanah={kelembaban_tanah} → LED OFF")

            except ValueError as ve:
                print(f"❌ Gagal konversi data ke float: {ve}")
            except Exception as e:
                print(f"❌ Error tak terduga: {e}")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n🛑 Dihentikan oleh pengguna.")
finally:
    if ser.is_open:
        ser.close()
        print("🔌 Koneksi serial ditutup.")
