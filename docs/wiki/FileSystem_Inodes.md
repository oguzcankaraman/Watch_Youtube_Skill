**Özet:** Unix dosya sistemlerinde her dosya bir inode ile temsil edilir. inode, metadata ve data block pointer'larını tutar; dizinler ise isim→inode numarası eşleme tablolarıdır.
**Kütüphaneler/Teknolojiler:** ext4, APFS, NTFS, inode, VFS (Virtual File System)
**Bağlantılar:** [[OperatingSystemFundamentals]], [[DeviceDrivers]]
**Kaynak Video:** [[Videos#MtxP2pyCvYA]] — How Operating Systems Work

---

## inode Yapısı

```
inode
├── metadata (boyut, tarih, izinler, sahip)
├── direct pointer 1  →  DATA BLOCK
├── direct pointer 2  →  DATA BLOCK
│   ...
├── direct pointer 12 →  DATA BLOCK
├── 1. seviye indirect pointer  →  [pointer block]  →  DATA BLOCK
├── 2. seviye indirect pointer  →  [pointer block]  →  [pointer block]  →  DATA BLOCK
└── 3. seviye indirect pointer  →  ...
```

- Küçük dosyalar: direct pointer'lar yeterlidir.
- Büyük dosyalar: indirect pointer zinciri kullanılır.

## Dizinler

Dizin, bir tablo dosyasıdır:

```
hello-world.txt  →  inode 69420
README.md        →  inode 12345
```

- Dizinler inode içerik değil, **isim→numara eşlemesi** tutar.
- Bu yüzden `mv` aynı dosya sisteminde anlık gerçekleşir (sadece tablo güncellenir).

## Hard Link

```
/home/user/docs/hello.txt      →  inode 69420
/home/user/backup/hello.txt    →  inode 69420  (aynı inode!)
```

- Aynı inode'a birden fazla dizin girişi işaret edebilir.
- İnode, `link count` (referans sayısı) tutar; count 0 olduğunda data block'lar serbest bırakılır.
- Hard link, sembolik link'ten farklıdır (symlink ayrı bir inode'dur, inode numarasına değil yola işaret eder).

---

**Kaynak:** [[OperatingSystemFundamentals]]
