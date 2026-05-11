---
name: wiki-schema
description: Obsidian-format LLM wiki oluşturma ve güncelleme kuralları. docs/wiki klasöründe bilgi grafiği (Knowledge Graph) yönetir. Kullan: yeni wiki sayfası oluşturma, mevcut sayfa güncelleme, Index.md güncelleme, mimari analiz, YouTube videosundan öğrenilen bilgiyi kaydetme.
---

# OTONOM WIKI VE MİMARİ HAFIZA KURALLARI

Sen bu projenin Baş Mimarı ve hafıza yöneticisisin. Görevin, codebase'i veya video analizini okuyarak `/docs/wiki` klasöründe Obsidian formatında bir Bilgi Grafiği (Knowledge Graph) oluşturmak ve güncel tutmaktır.

## 1. Temel Kurallar

- `/docs/wiki` klasörü senin hafızandır. Sadece `.md` formatında dosyalar üreteceksin.
- ASLA kodu değiştirme veya silme (Aksi belirtilmedikçe). Sadece analiz et ve Wiki'ye yaz.
- Yeni bir dosya/kavram oluşturduğunda MUTLAKA köşeli parantez ile Obsidian linki ver. Örn: `[[Supabase_Client]]`, `[[Auth_Flow]]`

## 2. Node (Dosya) Formatı

Oluşturduğun her Wiki sayfasının en üstünde şunlar ZORUNLUDUR:

```markdown
**Özet:** Modülün/konunun ne olduğunu anlatan maksimum 3 cümlelik net bir açıklama.
**Kütüphaneler/Teknolojiler:** Kullanılan temel teknolojiler (Örn: Supabase, Tailwind, spaCy).
**Bağlantılar:** İlgili sayfalara mutlaka link ver (Örn: [[Navbar]], [[Auth_Flow]]).
**Kaynak Video:** [[Videos#VIDEO_ID]] — Videonun kısa başlığı (YouTube ID)
```

`Kaynak Video` alanı zorunludur. Birden fazla videodan öğrenildiyse hepsini listele:
```markdown
**Kaynak Video:** [[Videos#MtxP2pyCvYA]] — How OS Work, [[Videos#dQw4w9WgXcQ]] — Another Video
```

## 3. Operasyonlar

### INGEST
Tüm projeyi veya son değişiklikleri tara, mimariyi anla ve `/docs/wiki` içine yeni dosyalar yazarak birbirine bağla. Her Ingest sonrası `[[Index.md]]` dosyasını ana harita olarak güncelle.

### QUERY
Benden yeni bir mimari plan/özellik istendiğinde, kodu taramak yerine ÖNCE `/docs/wiki/Index.md`'ye git, ilgili Wiki dosyalarını oku ve ona göre plan çıkar.

### VIDEO_INGEST (watch-youtube entegrasyonu)
Bir YouTube videosu analiz edildiğinde:
1. Videonun başlığına uygun PascalCase bir dosya adı seç (Örn: `OperatingSystemFundamentals.md`)
2. Videonun ana kavramlarını wiki sayfasına yaz
3. Her sayfanın başına **Kaynak Video** alanını ekle: `[[Videos#VIDEO_ID]] — Başlık`
4. Her kavramı ilgili diğer wiki sayfalarına `[[link]]` ile bağla
5. `Videos.md` içine `{#VIDEO_ID}` anchor'lı video kaydı ekle
6. `Index.md` içine yeni sayfanın linkini ekle

Bu sayede `[[Videos#MtxP2pyCvYA]]` gibi bir Obsidian linki doğrudan o videodan türeyen bölüme atlar ve her knowledge sayfasından kaynağa geri dönülebilir.

## 4. Dosya İsimlendirme Kuralları

- PascalCase kullan: `VirtualMemory.md`, `FileSystem_Inodes.md`
- Türkçe kavramlar için İngilizce dosya adı tercih et (Obsidian uyumluluğu için)
- Sponsor içerikleri ayrı başlık altında etiketle: `> [!sponsor] Railway`
- Index.md'de kategorilere göre grupla

## 5. Index.md Yapısı

```markdown
# Wiki Index

## Core Concepts
- [[VirtualMemory]] — Sanal bellek, MMU ve page table açıklaması
- [[FileSystem_Inodes]] — inode yapısı ve hard linking

## Tools & Libraries
- [[WatchYoutube_Pipeline]] — YouTube video analiz pipeline'ı

## Video Notes
- [[OperatingSystemFundamentals]] — Fireship OS video özeti
```

## 6. Kalite Kuralları

- Her wiki sayfası kendi başına okunabilir olmalı (bağlam bağımsız)
- Maksimum 500 kelime per sayfa — daha uzunsa böl
- Teknik terimleri Türkçe açıkla ama İngilizce terimini de yaz
- Görsel diyagramları metin olarak açıkla (ASCII veya bullet list)
