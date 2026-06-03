import streamlit as st
import simpy
import random
import pandas as pd
import plotly.express as px

# --- 1. ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Gelişmiş Yük Dengeleme ve Maliyet Analizi", layout="wide")
st.title("🛡️ Akıllı Yük Dengeleme, Auto-Scaling ve Maliyet Simülasyonu")

# Yan Menü Parametreleri
st.sidebar.header("🕹️ Kontrol Paneli")
algo_choice = st.sidebar.selectbox("Yük Dengeleme Algoritması", ["Least Connections", "Round Robin", "Random"])

veri_kaynagi = st.sidebar.radio("Veri Kaynağı Seçimi", ["Sentetik Üretim (Poisson)", "Gerçek Veri Seti (CSV)"])
uploaded_file = None
if veri_kaynagi == "Gerçek Veri Seti (CSV)":
    uploaded_file = st.sidebar.file_uploader("Bir Log Dosyası Yükle (CSV)", type=["csv"])
    if st.sidebar.button("Örnek CSV İndir"):
        ornek_veri = pd.DataFrame({"Gelis_Araligi": [random.expovariate(1.0) for _ in range(100)]})
        csv = ornek_veri.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(label="📥 İndir", data=csv, file_name='ornek_log.csv', mime='text/csv')

st.sidebar.divider()
ddos_mode = st.sidebar.toggle("🚨 DDoS Saldırısı Başlat!", value=False)

# YENİ: AUTO-SCALING EKLENDİ
auto_scale_mode = st.sidebar.toggle("📈 Otomatik Ölçeklendirme (Auto-Scaling)", value=False)
st.sidebar.info("Auto-Scaling açıksa, sistem darboğaz anında otomatik sunucu açar, rahatlayınca kapatır.")

# Eğer Auto-Scaling kapalıysa manuel çökertme yapılabilir
failover_test = []
if not auto_scale_mode:
    failover_test = st.sidebar.multiselect("Çökecek Sunucuları Seç (Failover)", [f"Sunucu-{i+1}" for i in range(10)])

# Sistem Kapasitesi (Maksimum 10 sunucu havuzu)
MAX_SERVERS = 35
sim_time = 100

# --- 2. SİSTEM MANTIĞI ---

class AdvancedServer:
    def __init__(self, env, name, is_active=True):
        self.env = env
        self.name = name
        self.resource = simpy.Resource(env, capacity=2)
        self.is_active = is_active # Sunucu açık mı kapalı mı?
        self.processed_count = 0
        self.active_time = 0 # Maliyet hesabı için çalışma süresi

    def process(self, request_id):
        yield self.env.timeout(random.uniform(0.1, 0.4))
        self.processed_count += 1

def load_balancer(env, servers, algo, log_data, real_data_df=None):
    request_id = 0
    rr_index = 0 
    
    if real_data_df is not None:
        istek_listesi = real_data_df['Gelis_Araligi'].tolist()
    else:
        istek_listesi = None

    while True:
        if ddos_mode:
            arrival_interval = 0.01 
        elif istek_listesi is not None:
            if request_id < len(istek_listesi):
                arrival_interval = istek_listesi[request_id]
            else:
                break 
        else:
            arrival_interval = random.expovariate(1.5)
            
        yield env.timeout(arrival_interval)
        request_id += 1
        
        # Sadece aktif (çöktürülmemiş ve Auto-Scale ile kapatılmamış) sunucular
        active_servers = [s for s in servers if s.is_active and s.name not in failover_test]
        
        if not active_servers:
            log_data.append({"Zaman": env.now, "Durum": "SİSTEM ÇÖKTÜ", "Hata": "Aktif Sunucu Yok"})
            continue

        selected_server = None
        if algo == "Least Connections":
            selected_server = min(active_servers, key=lambda s: len(s.resource.queue) + s.resource.count)
        elif algo == "Round Robin":
            selected_server = active_servers[rr_index % len(active_servers)]
            rr_index += 1
        else: 
            selected_server = random.choice(active_servers)

        env.process(handle_request(env, selected_server, request_id, log_data))

def handle_request(env, server, req_id, log_data):
    start_time = env.now
    try:
        with server.resource.request() as req:
            result = yield req | env.timeout(0.5) 
            
            if req in result:
                yield env.process(server.process(req_id))
                latency = env.now - start_time
                log_data.append({"Zaman": env.now, "Sunucu": server.name, "Gecikme": latency, "Durum": "Başarılı"})
            else:
                log_data.append({"Zaman": env.now, "Sunucu": server.name, "Gecikme": 0.5, "Durum": "Başarısız (Kuyrukta Düştü)"})
    except Exception:
        pass

# YENİ: SİSTEM İZLEME VE AUTO-SCALING MOTORU (Isı haritası ve otonom yönetim için)
def system_monitor(env, servers, monitor_data):
    while True:
        active_servers = [s for s in servers if s.is_active and s.name not in failover_test]
        total_queue = sum(len(s.resource.queue) for s in active_servers)
        
        # Saniye saniye log al (Isı haritası için)
        for s in active_servers:
            monitor_data.append({"Zaman": int(env.now), "Sunucu": s.name, "Kuyruk": len(s.resource.queue)})
            s.active_time += 1 # Maliyet için saniye sayacı
            
        # AUTO-SCALING MANTIĞI: Müşteriler çok bekliyorsa sunucu aç, boşsa kapat.
        if auto_scale_mode:
            if total_queue > len(active_servers) * 3 and len(active_servers) < MAX_SERVERS:
                # Darboğaz var! Kapalı olan ilk sunucuyu aç (Scale UP)
                inactive = [s for s in servers if not s.is_active]
                if inactive:
                    inactive[0].is_active = True
            elif total_queue == 0 and len(active_servers) > 2:
                # Trafik yok, boşa para yakmayalım. Son sunucuyu kapat (Scale DOWN)
                active_servers[-1].is_active = False

        yield env.timeout(1) # Her 1 saniyede bir kontrol et

# --- 3. ÇALIŞTIRMA VE GÖRSELLEŞTİRME ---

if st.sidebar.button("Simülasyonu Başlat"):
    log_data = []
    monitor_data = [] # Isı haritası verileri
    real_df = None
    
    if veri_kaynagi == "Gerçek Veri Seti (CSV)" and uploaded_file is not None:
        real_df = pd.read_csv(uploaded_file)
        
    env = simpy.Environment()
    
    # Auto-scale açıksa 2 sunucuyla başla gerisi kapalı olsun, kapalıysa 4 sunucuyla başla
    initial_active = 2 if auto_scale_mode else 4
    servers = [AdvancedServer(env, f"Sunucu-{i+1}", is_active=(i < initial_active)) for i in range(MAX_SERVERS)]
    
    env.process(load_balancer(env, servers, algo_choice, log_data, real_df))
    env.process(system_monitor(env, servers, monitor_data)) # Monitörü başlat
    env.run(until=sim_time)

    df = pd.DataFrame(log_data)
    df_monitor = pd.DataFrame(monitor_data)
    
    if "Gecikme" not in df.columns:
        st.error("🚨 SİSTEM TAMAMEN ÇÖKTÜ VEYA VERİ YOK!")
    else:
        # YENİ: FİNANSAL MALİYET DASHBOARD'U
        st.subheader("💰 Finansal Analiz ve Maliyet (Bulut Bilişim ROI)")
        col_m1, col_m2, col_m3 = st.columns(3)
        
        # Metrik Hesaplamaları
        toplam_sunucu_saniye = sum(s.active_time for s in servers)
        sunucu_maliyeti = toplam_sunucu_saniye * 0.05 # Saniyesi 0.05 Dolar
        basarisiz_istekler = len(df[df['Durum'] == 'Başarısız (Kuyrukta Düştü)'])
        ceza_maliyeti = basarisiz_istekler * 1.00 # Kaçan her müşteri 1 Dolar zarar
        toplam_zarar = sunucu_maliyeti + ceza_maliyeti
        
        col_m1.metric("Toplam Sunucu Maliyeti", f"${sunucu_maliyeti:.2f}", "Aktif Kalma Süresine Göre", delta_color="inverse")
        col_m2.metric("Müşteri Kaybı Zararı (Timeout)", f"${ceza_maliyeti:.2f}", f"{basarisiz_istekler} Kaçan İstek", delta_color="inverse")
        col_m3.metric("Toplam Operasyon Gideri", f"${toplam_zarar:.2f}", "Düşük olması iyidir", delta_color="inverse")
        st.divider()

        # GRAFİKLER
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("🚀 Gecikme (Latency) Analizi")
            fig = px.scatter(df, x="Zaman", y="Gecikme", color="Durum", 
                             color_discrete_map={"Başarılı": "#00CC96", "Başarısız (Kuyrukta Düştü)": "#EF553B"})
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.subheader("🔥 Sunucu Yükü Isı Haritası (Darboğaz Radarı)")
            if not df_monitor.empty:
                # Isı haritası için veriyi pivotla
                pivot_df = df_monitor.pivot_table(index='Sunucu', columns='Zaman', values='Kuyruk', aggfunc='mean')
                fig_heat = px.imshow(pivot_df, color_continuous_scale='YlOrRd', 
                                     labels=dict(color="Kuyruk Uzunluğu"))
                st.plotly_chart(fig_heat, use_container_width=True)

        st.info(f"💡 **Sistem Raporu:** Auto-Scaling {'aktif' if auto_scale_mode else 'kapalı'} durumdaydı. En yoğun anda sistem darboğazı ısı haritasında kızararak gösterilmiştir.")