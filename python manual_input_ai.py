import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import os

# --- 1. Inisialisasi Dataset ---
dataset_path = 'dataset_suhu_kelembaban.csv'

# Buat file dataset jika belum ada
if not os.path.exists(dataset_path):
    print("📁 Dataset belum ditemukan, membuat file baru...")
    df = pd.DataFrame(columns=['Suhu (°C)', 'Kelembaban (%)', 'Output (1=ON, 0=OFF)', 'Kelembaban Tanah'])
    df.to_csv(dataset_path, index=False)
else:
    df = pd.read_csv(dataset_path)

print(f"✅ Dataset dimuat. Jumlah data: {len(df)}")

# --- 2. Latih Model AI ---
if len(df) >= 5:
    X = df[['Suhu (°C)', 'Kelembaban (%)']]
    y = df['Output (1=ON, 0=OFF)']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = DecisionTreeClassifier(criterion='entropy', max_depth=4, random_state=0)
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"🎯 Akurasi Model: {acc*100:.2f}%")
else:
    model = None
    print("⚠️ Dataset terlalu sedikit. Tambahkan minimal 5 data untuk melatih model.")

# --- 3. Input Manual dan Simpan ---
print("\n✍️ Masukkan data manual (format: suhu, kelembaban_udara, kelembaban_tanah)")
print("📌 Contoh: 30.2,72.0,45.6")
print("Ketik 'exit' untuk keluar.\n")

while True:
    user_input = input("Masukkan data: ").strip()
    if user_input.lower() == 'exit':
        print("🚪 Program selesai.")
        break

    parts = user_input.split(',')
    if len(parts) != 3:
        print("❌ Format salah! Gunakan format: suhu,kelembaban_udara,kelembaban_tanah\n")
        continue

    try:
        suhu = float(parts[0].strip())
        kelembaban_udara = float(parts[1].strip())
        kelembaban_tanah = float(parts[2].strip())

        if model:
            input_data = pd.DataFrame([[suhu, kelembaban_udara]], columns=['Suhu (°C)', 'Kelembaban (%)'])
            prediksi = model.predict(input_data)[0]
        else:
            prediksi = 0  # default OFF jika model belum dilatih
            print("⚠️ Model belum tersedia, menggunakan default output 0 (OFF)")

        status = "ON (LED HIDUP)" if prediksi == 1 else "OFF (LED MATI)"
        print(f"📊 Prediksi: {prediksi} → {status}")

        # Simpan ke dataset
        new_row = pd.DataFrame([[suhu, kelembaban_udara, prediksi, kelembaban_tanah]],
                               columns=['Suhu (°C)', 'Kelembaban (%)', 'Output (1=ON, 0=OFF)', 'Kelembaban Tanah'])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(dataset_path, index=False)
        print("✅ Data disimpan.\n")

        # Latih ulang model setelah simpan (opsional)
        if len(df) >= 5:
            X = df[['Suhu (°C)', 'Kelembaban (%)']]
            y = df['Output (1=ON, 0=OFF)']
            model.fit(X, y)
    except ValueError:
        print("❌ Input tidak valid, pastikan format dan angka benar.\n")
