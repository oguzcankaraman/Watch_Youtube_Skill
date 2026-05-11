**Özet:** Device driver'lar, OS'un generic komutlarını donanıma özgü assembly talimatlarına çeviren yazılım katmanıdır. Kernel boot sırasında yüklenir ve Ring 0'da çalışır; bu yüzden hatalı driver tüm sistemi çökertebilir.
**Kütüphaneler/Teknolojiler:** Linux Kernel Modules, Windows WDM, ACPI, Ring 0
**Bağlantılar:** [[OperatingSystemFundamentals]], [[KernelMode_Ring0]]
**Kaynak Video:** [[Videos#MtxP2pyCvYA]] — How Operating Systems Work

---

## Neden Driver Gerekir?

```
OS  →  "print this pdf"  →  ??  →  PRINTER
```

OS her yazıcı markasının komut setini bilemez. Driver, bu soyutlama katmanını sağlar:

```
OS  →  generic_print(data)
         ↓
      DRIVER (yazıcıya özgü)
         ↓
      HP-specific assembly: 0xC4, 0x15, 0x6A...
         ↓
      PRINTER
```

## Driver Türleri (Örnek)

| Tür | Örnek |
|-----|-------|
| Grafik sürücüsü | NVIDIA, AMD GPU driver |
| Ses sürücüsü | Realtek HD Audio |
| Ağ sürücüsü | Intel Network Adapter |
| ACPI | Güç yönetimi |

## Neden Tehlikeli?

- Driver'lar **Ring 0 (kernel mode)** içinde çalışır.
- Bir hata → tüm OS çöker (**BSOD** / **Kernel Panic**).
- Windows BSOD'larının büyük çoğunluğu grafik sürücüsü kaynaklıdır.
- Linux'ta `modprobe` ile dinamik yükleme yapılabilir; hata izole edilebilir.

## Boot Sırası

```
Kernel yüklenir
    → ACPI driver'ları yüklenir
    → Storage driver'ları yüklenir
    → GPU driver'ları yüklenir
    → Kullanıcı alanı başlar (init/systemd)
```

---

**Kaynak:** [[OperatingSystemFundamentals]]
