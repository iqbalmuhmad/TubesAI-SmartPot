import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import serial
import time

# --- 1. Pelatihan Model Machine Learning ---

# Memuat dataset
try:
    df = pd.read_csv('dataset_suhu_kelembaban.csv')
    print("Dataset berhasil dimuat.")
except FileNotFoundError:
    print("Error: dataset_suhu_kelembaban.csv tidak ditemukan. Pastikan file berada di direktori yang sama.")
    exit()

# Menentukan fitur (X) dan target (y)
# Suhu dan Kelembaban udara sebagai fitur, Output sebagai target
# Kita tidak menggunakan kelembaban tanah dari dataset karena dataset hanya memiliki suhu dan kelembaban udara
X = df[['Suhu (°C)', 'Kelembaban (%)']]
y = df['Output (1=ON, 0=OFF)']

# Membagi data menjadi training dan testing set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Menginisialisasi model K-Nearest Neighbors (KNN)
# Anda bisa mencoba model lain seperti RandomForestClassifier atau LogisticRegression
model = KNeighborsClassifier(n_neighbors=3) # n_neighbors bisa disesuaikan

# Melatih model
model.fit(X_train, y_train)

# Evaluasi model (opsional, untuk melihat performa model)
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Akurasi model pada data test: {accuracy*100:.2f}%")

# --- 2. Komunikasi dengan Arduino dan Prediksi ---

# Konfigurasi serial port (sesuaikan dengan port Arduino Anda)
# Untuk menemukan port, buka Arduino IDE, pergi ke Tools > Port
# Contoh: 'COM3' di Windows, '/dev/ttyUSB0' atau '/dev/ttyACM0' di Linux/macOS
arduino_port = 'COM7' # Ganti dengan port Arduino Anda
baud_rate = 115200

try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"Terhubung ke Arduino di {arduino_port}")
    time.sleep(2) # Beri waktu Arduino untuk reset setelah koneksi serial
except serial.SerialException as e:
    print(f"Error: Tidak dapat terhubung ke Arduino di {arduino_port}. Pastikan port benar dan Arduino terhubung.")
    print(e)
    exit()

print("\nMembaca data dari Arduino dan mengirim perintah...")

try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"Data dari Arduino: {line}")

            # Pisahkan data suhu, kelembaban udara, dan kelembaban tanah
            try:
                parts = line.split(',')
                if len(parts) == 3:
                    suhu_arduino = float(parts[0])
                    kelembaban_udara_arduino = float(parts[1])
                    kelembaban_tanah_arduino = float(parts[2]) # Kelembaban tanah tidak digunakan dalam prediksi ML ini

                    # Buat DataFrame untuk prediksi (harus sesuai dengan format X_train)
                    # Perhatikan bahwa model hanya dilatih dengan Suhu dan Kelembaban udara
                    data_for_prediction = pd.DataFrame([[suhu_arduino, kelembaban_udara_arduino]],
                                                       columns=['Suhu (°C)', 'Kelembaban (%)'])

                    # Prediksi output menggunakan model ML
                    predicted_output = model.predict(data_for_prediction)[0]

                    # Kirim perintah ke Arduino
                    if predicted_output == 1:
                        ser.write(b'1\n')
                        print("Mengirim: 1 (LED ON)")
                    else:
                        ser.write(b'0\n')
                        print("Mengirim: 0 (LED OFF)")
                else:
                    print("Format data dari Arduino tidak sesuai (mengharapkan 3 nilai dipisahkan koma).")
            except ValueError:
                print("Error: Tidak dapat mengkonversi data dari Arduino ke float.")
            except Exception as e:
                print(f"Error saat memproses data Arduino: {e}")

        # Tambahkan delay agar tidak terlalu cepat membaca serial (opsional, tergantung kebutuhan)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nProgram dihentikan oleh pengguna.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Koneksi serial ditutup.")