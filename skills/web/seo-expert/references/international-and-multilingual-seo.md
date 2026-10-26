# International & Multilingual SEO Architecture

Managing multi-country and multilingual routing prevents duplicate content penalties and ensures searchers land on their localized language/currency variation.

## 1. URL Architecture for Global Sites

| Strategy | Structure | Pros | Cons | Recommendation |
|---|---|---|---|---|
| **Subdirectories (gTLD)** | `example.com/id/`, `example.com/en/` | Consolidated domain authority, cheap to maintain, single SSL. | Server routing complexity. | **Strongly Recommended** for modern SaaS and e-commerce. |
| **Subdomains** | `id.example.com`, `en.example.com` | Easy server isolation, flexible hosting. | Split domain authority; Google treats subdomains as distinct entities. | Acceptable when stacks differ wildly. |
| **ccTLDs** | `example.id`, `example.sg` | Strongest local trust and geo-signal. | Expensive, zero authority consolidation, high operational overhead. | Only for massive regional brands. |

---

## 2. Hreflang Tag Implementation

Hreflang instructs search engines which language/region version to serve:
```html
<link rel="alternate" hreflang="id" href="https://example.com/id/produk" />
<link rel="alternate" hreflang="en" href="https://example.com/en/product" />
<link rel="alternate" hreflang="x-default" href="https://example.com/en/product" />
```

### Golden Rules of Hreflang:
1. **Bidirectional Reciprocity:** If page A points to page B with `hreflang="en"`, page B MUST point back to page A with `hreflang="id"`. Unidirectional links are ignored by Google.
2. **Self-Referencing:** Each localized page must include a hreflang tag pointing to itself.
3. **The `x-default` Fallback:** Always declare `hreflang="x-default"` for unmapped or global fallback visitors (typically global English).
4. **Valid ISO Codes:** Use ISO 639-1 for language (e.g., `id`, `en`, `es`) and ISO 3166-1 Alpha 2 for country (e.g., `en-US`, `en-GB`, `id-ID`).

---

## 3. Indonesian Market Nuances (ID-Specific Search Behavior)
- **Informal & Slang Keywords:** Indonesian search volume heavily leans on conversational search terms (*"bengkel sepeda terdekat"*, *"cara pasang rd tanpa anting"*, *"rekomendasi velg murah awet"*).
- **WhatsApp Call to Action:** Local conversion funnels rely on direct WhatsApp CTAs (`https://wa.me/62821...`). Include microdata with phone contact.
- **Mobile-First Indexing:** Over 85% of Indonesian traffic originates on Android devices over 4G connections. Aggressive payload compression (< 1.5MB total page weight) directly impacts rank.
