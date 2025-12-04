import datetime
import time

# =============================================================================
# MOCK DATABASE (SIMULASI DATA MAHASISWA & TARIF)
# =============================================================================
# Ini adalah penerapan "Decomposition" - memisahkan data dari logika program.

# Database Mahasiswa terdaftar (NIM, Plat Nomor, Saldo Digital)
db_mahasiswa = {
    "D1234AB": {"nama": "Budi", "nim": "13521001", "saldo": 50000, "status_aktif": True, "jenis": "Motor"},
    "B5678CD": {"nama": "Siti", "nim": "18221005", "saldo": 10000, "status_aktif": True, "jenis": "Mobil"},
    # Plat yang terdaftar tapi saldo kurang
    "D9999XX": {"nama": "Joko", "nim": "10121099", "saldo": 1000, "status_aktif": True, "jenis": "Motor"}
}

# Database Transaksi Parkir (Menyimpan data kendaraan yang sedang parkir)
# Key: Plat Nomor / ID Kartu, Value: Waktu Masuk
db_parkir_aktif = {}

# Konfigurasi Tarif (Abstraction - detail angka disembunyikan dalam variabel)
TARIF_MOTOR_JAM_PERTAMA = 2000
TARIF_MOTOR_PER_JAM = 1000
TARIF_MOBIL_JAM_PERTAMA = 5000
TARIF_MOBIL_PER_JAM = 3000

# =============================================================================
# MODUL 1: SISTEM MASUK (ENTRY GATE)
# =============================================================================

def buka_palang_otomatis(metode):
    print(f"[GATE] Palang Terbuka! (Metode: {metode})")
    print("------------------------------------------------------")

def panggil_petugas(pesan_error):
    print(f"[ALARM] ERROR: {pesan_error}")
    print("[ALARM] Mohon tunggu, petugas sedang menuju lokasi...")
    print("------------------------------------------------------")

def proses_masuk(input_plat=None, input_kartu=None):
    """
    Mensimulasikan alur kendaraan masuk sesuai Flowchart 1.
    """
    print(f"\n>>> KENDARAAN TIBA DI GERBANG MASUK")
    waktu_masuk = datetime.datetime.now()
    
    # 1. Deteksi Plat Nomor (Prioritas Utama)
    if input_plat:
        print(f"[SENSOR] Mendeteksi Plat Nomor: {input_plat}")
        
        # Cek Database
        mahasiswa = db_mahasiswa.get(input_plat)
        
        if mahasiswa and mahasiswa['status_aktif']:
            print(f"[SISTEM] Identitas Terkonfirmasi: {mahasiswa['nama']} ({mahasiswa['nim']})")
            
            # Simpan data masuk
            db_parkir_aktif[input_plat] = {
                "waktu_masuk": waktu_masuk,
                "jenis": mahasiswa['jenis'],
                "metode_masuk": "PLAT_NOMOR"
            }
            buka_palang_otomatis("Scan Plat Nomor")
            return # Selesai, keluar fungsi
        else:
            print("[SISTEM] Plat tidak dikenali atau tidak terdaftar.")
    else:
        print("[SENSOR] Plat Nomor Tidak Terbaca/Kotor.")

    # 2. Fallback ke Manual (Tap Kartu)
    print("[INSTRUKSI] Silakan Tempel Kartu E-Money Anda...")
    
    if input_kartu:
        # Simulasi tap kartu berhasil
        print(f"[READER] Membaca Kartu ID: {input_kartu}")
        
        # Simpan data masuk (Asumsi tamu/manual pakai tarif Mobil default jika tidak tahu)
        db_parkir_aktif[input_kartu] = {
            "waktu_masuk": waktu_masuk,
            "jenis": "Mobil", # Default untuk tamu
            "metode_masuk": "KARTU"
        }
        buka_palang_otomatis("Tap Kartu Manual")
    else:
        # Jika tap kartu juga gagal
        panggil_petugas("Gagal Tap Kartu / Kartu Rusak")

# =============================================================================
# MODUL 2: SISTEM KELUAR & BAYAR (EXIT GATE)
# =============================================================================

def hitung_durasi(waktu_masuk, waktu_keluar):
    """Menghitung selisih jam (dibulatkan ke atas)"""
    selisih = waktu_keluar - waktu_masuk
    total_detik = selisih.total_seconds()
    jam = int(total_detik // 3600)
    if (total_detik % 3600) > 0:
        jam += 1
    return jam

def hitung_tarif(durasi, jenis_kendaraan):
    """
    Penerapan 'Pattern Recognition': Pola perhitungan tarif berjenjang.
    """
    if durasi <= 0: return 0
    
    total_bayar = 0
    
    if jenis_kendaraan == "Motor":
        total_bayar = TARIF_MOTOR_JAM_PERTAMA + ((durasi - 1) * TARIF_MOTOR_PER_JAM)
    elif jenis_kendaraan == "Mobil":
        total_bayar = TARIF_MOBIL_JAM_PERTAMA + ((durasi - 1) * TARIF_MOBIL_PER_JAM)
        
    return total_bayar

def proses_keluar(id_identitas, saldo_kartu_fisik=0):
    """
    Mensimulasikan alur kendaraan keluar sesuai Flowchart 2.
    id_identitas bisa berupa Plat Nomor atau ID Kartu.
    """
    print(f"\n>>> KENDARAAN DI POS KELUAR (ID: {id_identitas})")
    
    # 1. Ambil Data Masuk
    data_parkir = db_parkir_aktif.get(id_identitas)
    
    if not data_parkir:
        print("[ERROR] Data masuk tidak ditemukan! Tiket hilang?")
        return

    # Simulasi waktu keluar (anggap parkir 3 jam kemudian untuk demo)
    waktu_masuk = data_parkir['waktu_masuk']
    waktu_keluar = waktu_masuk + datetime.timedelta(hours=3, minutes=15) # Simulasi 4 jam
    
    # 2. Hitung Durasi & Tarif (Abstraction)
    durasi = hitung_durasi(waktu_masuk, waktu_keluar)
    jenis = data_parkir['jenis']
    tagihan = hitung_tarif(durasi, jenis)
    
    print(f"[INFO] Durasi Parkir: {durasi} Jam ({jenis})")
    print(f"[TAGIHAN] Total Biaya: Rp {tagihan}")
    
    # 3. Proses Pembayaran
    # Cek apakah ini mahasiswa terdaftar (punya saldo digital)
    mahasiswa = db_mahasiswa.get(id_identitas)
    
    pembayaran_sukses = False
    
    # Opsi A: Bayar pakai Saldo Mahasiswa (Prioritas)
    if mahasiswa:
        print(f"[BAYAR] Mencoba autodebet saldo mahasiswa (Sisa: Rp {mahasiswa['saldo']})...")
        if mahasiswa['saldo'] >= tagihan:
            mahasiswa['saldo'] -= tagihan
            print(f"[SUKSES] Pembayaran Berhasil! Sisa Saldo: Rp {mahasiswa['saldo']}")
            pembayaran_sukses = True
        else:
            print("[GAGAL] Saldo Digital tidak cukup.")
    
    # Opsi B: Bayar pakai Kartu E-Money (Fallback)
    if not pembayaran_sukses:
        print("[BAYAR] Silakan tempel Kartu E-Money...")
        print(f"[INFO] Saldo Kartu Fisik terbaca: Rp {saldo_kartu_fisik}")
        
        if saldo_kartu_fisik >= tagihan:
            saldo_kartu_fisik -= tagihan
            print(f"[SUKSES] Pembayaran Kartu Berhasil! Sisa Saldo Kartu: Rp {saldo_kartu_fisik}")
            pembayaran_sukses = True
        else:
            print("[GAGAL] Saldo Kartu juga kurang!")
            panggil_petugas("Gagal Bayar (Saldo Habis)")
            return

    if pembayaran_sukses:
        # Hapus dari data parkir aktif
        del db_parkir_aktif[id_identitas]
        buka_palang_otomatis("Keluar")

# =============================================================================
# MAIN PROGRAM (SIMULASI SKENARIO)
# =============================================================================

if __name__ == "__main__":
    print("=== SIMULASI SISTEM PARKIR TOUCHLESS ITB ===")
    
    # SKENARIO 1: Mahasiswa Motor (Saldo Cukup, Plat Terbaca)
    # Ekspektasi: Masuk mulus, Keluar potong saldo digital
    proses_masuk(input_plat="D1234AB")
    proses_keluar("D1234AB") 
    
    # SKENARIO 2: Mahasiswa Mobil (Saldo Kurang)
    # Ekspektasi: Masuk mulus, Keluar gagal autodebet -> Minta Kartu
    proses_masuk(input_plat="D9999XX")
    proses_keluar("D9999XX", saldo_kartu_fisik=50000) # User punya kartu fisik saldo 50rb
    
    # SKENARIO 3: Tamu / Plat Tidak Terbaca
    # Ekspektasi: Masuk minta kartu, Keluar bayar kartu
    proses_masuk(input_plat=None, input_kartu="CARD-001")
    proses_keluar("CARD-001", saldo_kartu_fisik=20000)
