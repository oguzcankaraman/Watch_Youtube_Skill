**Özet:** Bu video işletim sisteminin temel bileşenlerini anlatıyor: süreçler ve multitasking, kernel modu (Ring 0), sanal bellek ve MMU, dosya sistemi (inode/hard link) ve device driver'lar. CPU'nun tek bir hard-coded adresten boot ettiğini ve kernel'in C ile yazıldığını gösteriyor.
**Kütüphaneler/Teknolojiler:** Linux Kernel, C (Ring 0), MMU/Page Table, inode File System, Device Drivers
**Bağlantılar:** [[VirtualMemory_PageTable]], [[FileSystem_Inodes]], [[DeviceDrivers]], [[KernelMode_Ring0]]
**Kaynak Video:** [[Videos#MtxP2pyCvYA]] — How Operating Systems Work

---

## 1. Süreçler ve Multitasking

- Görünürde aynı anda çalışan onlarca süreç vardır (Chrome'un 13 ayrı process'i).
- Fare hareketi arka planda bile çalışır — bu CPU'nun hızlı context-switching yapmasından kaynaklanır.
- Tek bir fiziksel CPU çekirdeği bile bu yanılsamayı yaratabilir.

## 2. Boot ve Kernel Handoff

- CPU açılışta **hard-coded bir adrese** atlar (BIOS/UEFI).
- Bootloader → Kernel zinciri: kernel yüklendiğinde CPU tam donanım erişimiyle kernel kodunu çalıştırır.
- Bu noktaya kadar hiçbir kullanıcı uygulaması çalışmaz.

## 3. Kernel Modu — Ring 0

```
Ring 0  →  Kernel (C kodu, tam donanım erişimi)
Ring 3  →  Kullanıcı uygulamaları (kısıtlı)
```

- Kernel, **C** ile yazılmıştır ve **Ring 0** ayrıcalığıyla çalışır.
- Kullanıcı uygulamaları donanıma doğrudan erişemez; sistem çağrısı (syscall) yapmaları gerekir.

## 4. Sanal Bellek ve MMU

Bkz. → [[VirtualMemory_PageTable]]

- Her process, **kendi sanal adres alanına** sahiptir.
- **MMU (Memory Management Unit)** virtual → physical adres çevirisini yapar.
- Her process için ayrı **page table** vardır (4 KB'lık sayfalar).
- Chrome ve 1Password aynı sanal adreste farklı fiziksel belleğe işaret edebilir → izolasyon sağlanır.

## 5. Dosya Sistemi ve inode'lar

Bkz. → [[FileSystem_Inodes]]

- Her dosya bir **inode** ile temsil edilir: metadata + direct/indirect pointer'lar → data block'lar.
- **Dizinler** inode numaralarına işaret eden isim→numara eşleme tablolarıdır.
- **Hard link**: Aynı inode'a birden fazla dizin girişi işaret edebilir (örn. inode `69420`).
- File system mimarileri çeşitlilik gösterir (ext4, NTFS, APFS vb.).

## 6. Device Driver'lar

Bkz. → [[DeviceDrivers]]

```
OS  →  "print this pdf"  →  DRIVER  →  Yazıcıya özgü assembly komutları  →  PRINTER
```

- OS yazıcının dilini bilmez; **driver** katmanı generic komutu donanım talimatına çevirir.
- Kernel boot sırasında device driver'ları yükler.
- Hatalı driver → **BSOD** (Windows Blue Screen of Death) — en sık grafikler sürücülerinden kaynaklanır.

## 7. Sponsor — Railway

> [!sponsor] Railway
> Video ortasında Railway cloud deployment platformu tanıtılıyor. `railway.yaml` ile repo bağlanabiliyor. Railway CLI, **Codex, Claude Code, Cursor, Gemini CLI, GitHub Copilot** gibi AI agent skill'leri destekliyor.

---

**Kaynak:** YouTube `MtxP2pyCvYA` — Fireship tarzı OS fundamentals videosu (~6.5 dak.)
**Analiz tarihi:** 2026-05-09
**Storyboard:** `output/storyboard_page_001.jpg`, `_002.jpg`, `_003.jpg` — 20 kare, 3 sayfa
