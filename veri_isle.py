import pandas as pd

print("⏳ Gerçek veri işleniyor...")

# DİKKAT: Burada örnek olsun diye gerçek bir web sitesinin zaman damgalarını manuel girdim.
# Normalde buraya: df = pd.read_csv("internetten_indirdigim_veri.csv") yazılır.
gercek_istek_saatleri = {
    "Zaman": [
        "2023-11-24 10:00:00.000",
        "2023-11-24 10:00:01.500",  # 1.5 sn sonra
        "2023-11-24 10:00:03.000",  # 1.5 sn sonra
        "2023-11-24 10:00:03.100",  # 0.1 sn (Yoğunluk başlıyor)
        "2023-11-24 10:00:03.150",  # 0.05 sn (DDoS veya Kampanya anı!)
        "2023-11-24 10:00:03.180",  # 0.03 sn 
        "2023-11-24 10:00:05.000",  # 1.82 sn (Trafik rahatladı)
        "2023-11-24 10:00:07.500",  # 2.5 sn sonra
    ]
}

# Veriyi Pandas DataFrame'e çeviriyoruz
df = pd.DataFrame(gercek_istek_saatleri)

# 1. Metin halindeki saatleri gerçek "Tarih/Saat (Datetime)" formatına çevir
df['Zaman'] = pd.to_datetime(df['Zaman'])

# 2. İki satır arasındaki SÜRE FARKINI (.diff) hesapla ve saniyeye çevir
df['Gelis_Araligi'] = df['Zaman'].diff().dt.total_seconds()

# 3. İlk satırın kendisinden öncesi olmadığı için boş (NaN) kalır, onu siliyoruz
df = df.dropna()

# 4. Sadece 'Gelis_Araligi' sütununu al ve simülasyonun okuması için CSV olarak kaydet
df[['Gelis_Araligi']].to_csv("gercek_log_verisi.csv", index=False)

print("✅ İşlem tamam! 'gercek_log_verisi.csv' dosyası başarıyla oluşturuldu.")
