# Tugas 1 — Analisis Pitfall FoodGo

**Kelompok 7:**

| Nama | NIM | Kontribusi |
|---|---|---|
| Aria Restu Pambudi | 103072400168 | Pitfall 1 |
| Bagas Dwi Andra | 103072400144 | Pitfall 3 |
| Brian Alfredo Adhita Putra | 103072400165 | Pitfall 3 |
| M Gibran Khalilullah | 103072400014 | Pitfall 2 |

## Pitfall 1: The Network Is Reliable — ditulis oleh Aria Restu Pambudi

**Bukti di skenario:** 
Kode FoodGo berisi asumsi `# network is always reliable, no need for retry`. Tidak ada mekanisme penanganan kegagalan saat modul pesanan memanggil modul pembayaran.

**Kenapa ini keliru:** 
Dalam sistem terdistribusi, paket bisa hilang, koneksi bisa putus, dan service tujuan bisa sedang restart atau overload. Kegagalan sementara (transient failure) adalah kondisi normal, terutama saat trafik tinggi, sehingga harus dirancang sejak awal.

**Dampak ke FoodGo:** 
Satu panggilan ke modul pembayaran yang gagal sesaat langsung menjadi pesanan gagal. Tanpa retry, pelanggan harus mengulang dari awal. Kondisi ini paling sering terjadi saat jam makan siang atau promo, yaitu saat jaringan dan service paling tertekan.

**Solusi desain awal:** 
Terapkan retry dengan exponential backoff + jitter hanya untuk operasi yang aman diulang. Buat pembayaran bersifat idempotent dengan idempotency key agar retry tidak menyebabkan pelanggan ditagih dua kali. Tambahkan circuit breaker agar service yang sedang bermasalah tidak terus dipanggil.

**Trade-off:** 
Retry yang tidak terkendali justru memperparah beban saat service sudah kewalahan (retry storm, cascading failure). Karena itu retry harus dibatasi jumlahnya, diberi jitter, dan dipasangkan dengan circuit breaker. Idempotency juga menambah kompleksitas implementasi dan penyimpanan state.

---

## Pitfall 2: Latency is Zero (tanpa timeout pada panggilan antar service) — ditulis oleh Brian Alfredo dan Bagas Dwi Andra

**Bukti di skenario:**
Tidak ada timeout sama sekali pada pemanggilan antar service. Modul pesanan memanggil modul pembayaran dan menunggu tanpa batas waktu. Gejalanya: aplikasi sangat lambat, beberapa permintaan timeout, dan server kadang crash total.

**Kenapa ini keliru:**
Panggilan jaringan tidak seperti pemanggilan fungsi lokal. Latensinya bervariasi dan bisa melonjak tak terbatas saat beban tinggi. Menunggu tanpa batas berarti menggantungkan resource sendiri pada kecepatan pihak lain.

**Dampak ke FoodGo:**
Saat modul pembayaran melambat, setiap request pesanan menahan satu thread atau koneksi sambil menunggu. Request baru terus masuk, thread pool dan memori habis, lalu modul pesanan ikut tidak responsif dan akhirnya server crash. Jadi lambatnya satu komponen merembet menjadi kegagalan total (cascading failure) dan perlu restart manual.

**Solusi desain awal:** 
Pasang timeout pada semua panggilan antar service, dengan nilai berdasarkan latensi normal (misalnya persentil ke-99 ditambah margin). Gunakan bulkhead (thread pool atau koneksi terpisah per dependensi) agar pembayaran yang lambat tidak menghabiskan resource modul pesanan. Untuk proses yang tidak harus real-time, seperti notifikasi kurir, gunakan komunikasi asinkron lewat message queue.

**Trade-off:** 
Timeout yang terlalu pendek menyebabkan false failure, yaitu request yang sebenarnya akan sukses malah dibatalkan, dan ini bisa memicu retry yang menambah beban. Timeout yang terlalu panjang tidak melindungi sistem. Komunikasi asinkron membuat sistem eventually consistent, sehingga pengguna tidak langsung melihat status final dan alur kerja menjadi lebih sulit di-debug.

## Pitfall 3: [nama pitfall] — ditulis oleh [nama]

(ulangi struktur di atas)

---

## Kesimpulan Kelompok

[Ringkasan: jika FoodGo memperbaiki ketiga pitfall ini, apa arsitektur yang disarankan secara garis besar? Kaitkan dengan Tugas 2.]
