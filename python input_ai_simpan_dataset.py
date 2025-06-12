import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import os

# --- Konfigurasi ---
K = 3  # Jumlah tetangga pada KNN
dataset_path = 'dataset_suhu_kelembaban.csv'

# --- Cek atau buat dataset jika belum ada ---
if not os.path.exists(dataset_path):
    print("📁 Dataset belum ada, membuat file baru...")
    df = pd.DataFrame(columns=['Suhu (°C)', 'Kelembaban (%)', 'Output (1=ON, 0=OFF)'])
    df.to_csv(dataset_path, index=False)
else:
    df = pd.read_csv(dataset_path)

print("✅ Dataset berhasil dimuat. Jumlah data saat ini:", len(df))

# --- 1. Latih Model KNN ---
if len(df) < K:
    print(f"⚠️ Dataset terlalu sedikit untuk model K={K}. Tambahkan data lebih banyak terlebih dahulu.")
else:
    X = df[['Suhu (°C)', 'Kelembaban (%)']]
    y = df['Output (1=ON, 0=OFF)']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = KNeighborsClassifier(n_neighbors=K, metric='euclidean')
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"🎯 Akurasi model saat ini: {accuracy*100:.2f}%\n")

# --- 2. Input Manual dan Simpan ke Dataset ---
print("✍️ Masukkan data manual (suhu, kelembaban udara, kelembaban tanah):")
print("📌 Format: 28.5,74.0,0.0")
print("Ketik 'exit' untuk keluar.\n")

while True:
    try:
        user_input = input("Masukkan data: ").strip()
        if user_input.lower() == 'exit':
            print("🚪 Keluar dari program.")
            break

        parts = user_input.split(',')
        if len(parts) != 3:
            print("⚠️ Format salah. Gunakan: suhu,kelembaban_udara,kelembaban_tanah")
            continue

        suhu = float(parts[0])
        kelembaban_udara = float(parts[1])
        kelembaban_tanah = float(parts[2])  # tidak dipakai dalam prediksi, tapi bisa disimpan nanti jika ingin

        if len(df) >= K:
            # Prediksi menggunakan model
            input_data = pd.DataFrame([[suhu, kelembaban_udara]], columns=['Suhu (°C)', 'Kelembaban (%)'])
            predicted_output = model.predict(input_data)[0]
            status = "ON (LED HIDUP)" if predicted_output == 1 else "OFF (LED MATI)"
            print(f"📊 Prediksi Output AI: {predicted_output} → {status}")
        else:
            predicted_output = 0  # default
            print("⚠️ Model belum bisa memprediksi karena data kurang. Menyimpan data dengan Output = 0")

        # Tambahkan ke dataset dan simpan
        new_row = pd.DataFrame([[suhu, kelembaban_udara, predicted_output]], 
                               columns=['Suhu (°C)', 'Kelembaban (%)', 'Output (1=ON, 0=OFF)'])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(dataset_path, index=False)
        print("✅ Data disimpan ke dataset.\n")

    except ValueError:
        print("❌ Input harus berupa angka dengan format yang benar.\n")
