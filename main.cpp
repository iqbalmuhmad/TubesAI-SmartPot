#include <Arduino.h>
#include "DHT.h"

// Konfigurasi pin
#define DHTPIN 33         // DHT11 di GPIO33
#define DHTTYPE DHT11     // Tipe sensor DHT
#define SOIL_PIN 34       // Sensor tanah analog di GPIO34
#define LED_PIN 13        // LED sebagai aktuator

// Inisialisasi objek DHT
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);       // Inisialisasi komunikasi serial
  dht.begin();                // Mulai DHT
  pinMode(LED_PIN, OUTPUT);   // LED output
  digitalWrite(LED_PIN, LOW); // Matikan LED di awal
}

void loop() {
  // Baca dari sensor
  float suhu = dht.readTemperature();        // Suhu dalam Celsius
  float kelembaban = dht.readHumidity();     // Kelembaban udara (%)
  int adcSoil = analogRead(SOIL_PIN);        // Nilai ADC 0–4095

  // Ubah nilai ADC kelembaban tanah menjadi persentase (0–100%)
  // Asumsi: 0 = sangat basah, 4095 = sangat kering
  float kelembabanTanah = 100.0 - ((adcSoil / 4095.0) * 100.0);

  // Validasi hasil DHT
  if (!isnan(suhu) && !isnan(kelembaban)) {
    Serial.print(String(suhu, 1)); Serial.print(",");               // Suhu dengan 1 angka di belakang koma
    Serial.print(String(kelembaban, 1)); Serial.print(",");         // Kelembaban udara dengan 1 angka di belakang koma
    Serial.println(String(kelembabanTanah, 1));                     // Kelembaban tanah sebagai persentase
  } else {
    Serial.println("Error membaca sensor DHT");
  }

  // Tunggu data dari komputer (maks 2 detik)
  unsigned long startTime = millis();
  while (!Serial.available() && millis() - startTime < 2000) {
    delay(10);
  }

  // Jika ada data masuk, proses
  if (Serial.available()) {
    String hasil = Serial.readStringUntil('\n');
    hasil.trim();  // Hilangkan spasi/newline

    if (hasil == "1") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("LED ON");
    } else if (hasil == "0") {
      digitalWrite(LED_PIN, LOW);
      Serial.println("LED OFF");
    } else {
      Serial.println("Data tidak dikenali");
    }
  }

  delay(1000); // Tunggu 1 detik
}
