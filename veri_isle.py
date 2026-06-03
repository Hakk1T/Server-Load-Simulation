import pandas as pd

print("⏳ Gerçek veri işleniyor...")

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

df = pd.DataFrame(gercek_istek_saatleri)

df['Zaman'] = pd.to_datetime(df['Zaman'])

df['Gelis_Araligi'] = df['Zaman'].diff().dt.total_seconds()

df = df.dropna()

df[['Gelis_Araligi']].to_csv("gercek_log_verisi.csv", index=False)

print("✅ İşlem tamam! 'gercek_log_verisi.csv' dosyası başarıyla oluşturuldu.")
