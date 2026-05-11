# Open Design

**Özet:** Claude Design'ın ücretsiz, açık kaynaklı ve tamamen yerel (local) alternatifi; birden fazla AI agent CLI ile çalışarak UI, landing page ve slide deck üretir.

**Teknolojiler:** Node.js 24+, pnpm, Electron, SQLite, MCP, Agent CLI (Gemini CLI / Claude Code / Kilo Code / Codeex / Codex)

**Bağlantılar:** [[ClaudeDesignVsOpenDesign]], [[AgentCLIComparison]]

**Kaynak Video:** [Open Design — Free Local Claude Design Alternative](https://www.youtube.com/watch?v=8XcbyliBwc4) (`8XcbyliBwc4`)

---

## Nedir?

Open Design, Anthropic'in **Claude Design** ürününün açık kaynak, local-first alternatifidir. Claude Design abonelik (Individual / Team / Enterprise planları) gerektirirken Open Design tamamen ücretsiz ve kendi makinende çalışır.

Öne çıkan fark: **"Agent'ı yaratıcı bir iş birliği aracı olarak ele alır, kara kutu olarak değil."**

---

## Temel Özellikler

| Özellik | Detay |
|---|---|
| **Local-first** | Hiçbir şey buluta gönderilmez; tüm işlem kendi makinende |
| **Multi-agent** | Gemini CLI, Claude Code, Kilo Code, Codeex, Codex ile çalışır |
| **12 Agent Adapter** | Her katmanda farklı agent desteği |
| **31 Skill + 72 Design System** | İlk açılışta otomatik yüklenir |
| **Çıktı kalitesi** | Claude Design ile karşılaştırılabilir seviyede |
| **Export pipeline** | HTML, PDF, ZIP çıktısı |
| **Prototip şablonları** | dating-web, digital-guide, email-marketing, gamified-app |

---

## Neler Üretebilir?

- Tam landing page (animasyonlu)
- Slide deck
- UI prototipleri (mobil, web, dashboard)
- E-posta şablonları
- Dijital e-kitap / rehber kapakları

---

## Kurulum

```bash
git clone https://github.com/nnew-in/open-design.git
cd open-design
corepack enable
pnpm install
pnpm tools-dev run web
# Terminale yazdırılan URL'yi aç (örn. localhost:1033)
```

**Gereksinimler:** Node 24+, pnpm 10.33.2+

---

## İlk Çalıştırma

1. Hangi agent CLI'ların kurulu olduğunu otomatik algılar
2. 31 skill + 72 design system yükler
3. Anthropic API key paste edebileceğin hoş geldin diyaloğu açar (opsiyonel)
4. `./od/` klasörünü (local runtime, gitignored) otomatik oluşturur — `git init` gerekmez

---

## Claude Design ile Farkı

| | Claude Design | Open Design |
|---|---|---|
| **Fiyat** | Ücretli abonelik | Ücretsiz |
| **Çalışma modu** | Cloud-only | Local (yerel) |
| **Agent desteği** | Sadece Claude | Gemini, Claude Code, Kilo, Codeex, Codex… |
| **Kaynak kodu** | Kapalı | Apache 2.0 açık kaynak |
| **Çevrimdışı** | Hayır | Evet |
