**Özet:** Sanal bellek, her process'e izole bir adres alanı verir; MMU bu adresleri fiziksel RAM'e çevirir. Page table, process başına tutulur ve 4 KB'lık sayfalar halinde haritalama yapar.
**Kütüphaneler/Teknolojiler:** MMU (Hardware), Page Table, Linux Virtual Memory, TLB
**Bağlantılar:** [[OperatingSystemFundamentals]], [[KernelMode_Ring0]]
**Kaynak Video:** [[Videos#MtxP2pyCvYA]] — How Operating Systems Work

---

## Temel Kavramlar

| Kavram | Açıklama |
|--------|----------|
| Virtual Address | Process'in "gördüğü" adres — her process 0'dan başlar |
| Physical Address | RAM'deki gerçek konum |
| Page Table | Virtual → Physical eşleme tablosu (process başına) |
| MMU | Hardware birimi; her bellek erişiminde çeviri yapar |
| Page | 4 KB'lık bellek birimi |

## Çalışma Mantığı

```
Process A: virtual 0x1000  →  (Page Table A)  →  physical 0xA000
Process B: virtual 0x1000  →  (Page Table B)  →  physical 0xF000
```

İki process aynı virtual adresi kullanabilir ama farklı fiziksel belleğe işaret eder → **tam izolasyon**.

## Neden Önemli?

- Chrome bir process'e crash olduğunda diğer process'lerin belleğini bozamaz.
- Kernel, kullanıcı process'lerinin kernel belleğine erişmesini page table flags ile engeller.
- Swap (disk ↔ RAM taşıma) de page granülaritesinde yapılır.

---

**Kaynak:** [[OperatingSystemFundamentals]]
