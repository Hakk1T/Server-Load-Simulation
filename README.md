# 🌐 Akıllı Yük Dengeleme, Auto-Scaling ve Maliyet Simülasyonu

Bu proje, dağıtık sunucu ağlarında (Load Balancing) web isteklerinin nasıl yönetildiğini, siber saldırı (DDoS) altındaki davranışlarını ve bulut maliyet (Cost) analizlerini modelleyen interaktif bir sistem mühendisliği simülasyonudur. Mersin Üniversitesi, Bilişim Sistemleri ve Teknolojileri bölümü "Benzetim Programları" dersi vize projesi kapsamında geliştirilmiştir.

## 🚀 Projenin Amacı
Sistem; web sunucularına gelen anlık yüksek trafiği (kampanyalar, DDoS vb.) dengelemeyi, darboğazları (bottleneck) tespit etmeyi ve **Otomatik Ölçeklendirme (Auto-Scaling)** mantığıyla müşteri kaybı zararı ile bulut sunucu maliyeti arasındaki en optimum (kârlı) noktayı bulmayı amaçlamaktadır.

## ✨ Öne Çıkan Özellikler
* **Trace-Driven Simulation (Gerçek Veri):** Sadece matematiksel formüllerle (Poisson) değil, geçmişte yaşanmış gerçek web sunucusu erişim kayıtlarının (HTTP Log) CSV olarak yüklenip simüle edilmesi.
* **Auto-Scaling (Otonom Ölçeklendirme):** Sistem tıkandığında otomatik olarak yeni sunucuların devreye alınması (Scale-Up) ve trafik rahatladığında kapatılması (Scale-Down).
* **Finansal ROI Dashboard:** AWS/Azure benzeri bulut fiyatlandırması üzerinden anlık maliyet ve müşteri kaybı zararı analizi.
* **Canlı Isı Haritası (Heatmap):** Sunucu kuyruklarının darboğaz anlarını gösteren canlı radar.

## 🛠️ Kullanılan Teknolojiler
* **Python 3.x**
* **SimPy:** Ayrık-Olay (Discrete-Event) zaman ve kuyruk simülasyon motoru.
* **Streamlit:** Web tabanlı, interaktif kullanıcı arayüzü (GUI).
* **Pandas:** Veri ön işleme (Data Preprocessing) ve log analizi.
* **Plotly:** Canlı gecikme (latency) analizleri ve interaktif veri görselleştirme.

## ⚙️ Kurulum ve Çalıştırma

1. Projeyi bilgisayarınıza klonlayın:
```bash
git clone [https://github.com/Hakk1T/Server-Load-Simulation.git](https://github.com/Hakk1T/Server-Load-Simulation.git)
cd Server-Load-Simulation

2.Gerekli kütüphaneleri yükleyin:

pip install -r requirements.txt

3.Simülasyonu başlatın:

streamlit run app.py

📂 Proje Yapısı
app.py: Ana simülasyon motoru ve Streamlit arayüz kodları.

veri_isle.py: Ham zaman damgalarını (Timestamp) simülasyonun okuyabileceği saniye farklarına (diff) dönüştüren ön işleme scripti.

gercek_log_verisi.csv: Sistemin test edildiği örnek gerçek dünya veri seti.

requirements.txt: Proje bağımlılıkları.
