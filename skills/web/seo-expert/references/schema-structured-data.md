# Schema.org Structured Data & Rich Snippets

Structured data written in JSON-LD formats provides explicit machine-readable context to search bots and AI answer engines, qualifying the page for Rich Results (stars, FAQs, pricing, sitelinks search box).

Always inject structured data as `<script type="application/ld+json">` inside the HTML `<head>`.

---

## 1. Organization & WebSite (Global Homepage)

Establishes entity identity, logo, social profiles, and Google Sitelinks Search Box:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://www.example.com/#organization",
      "name": "Acme Digital",
      "url": "https://www.example.com",
      "logo": {
        "@type": "ImageObject",
        "url": "https://www.example.com/assets/logo.png",
        "width": 600,
        "height": 60
      },
      "sameAs": [
        "https://twitter.com/acmedigital",
        "https://www.instagram.com/acmedigital",
        "https://github.com/acmedigital"
      ]
    },
    {
      "@type": "WebSite",
      "@id": "https://www.example.com/#website",
      "url": "https://www.example.com",
      "name": "Acme Digital",
      "publisher": {
        "@id": "https://www.example.com/#organization"
      },
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://www.example.com/search?q={search_term_string}",
        "query-input": "required name=search_term_string"
      }
    }
  ]
}
</script>
```

---

## 2. Article / Blog Posting (Editorial Content)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Panduan Restorasi Sepeda Minion Phoenix Klasik",
  "description": "Langkah demi langkah merestorasi sepeda minion jadul dengan transmisi 7-speed dan rem kustom.",
  "image": "https://www.example.com/images/minion-cover.jpg",
  "datePublished": "2026-10-23T08:00:00+07:00",
  "dateModified": "2026-10-23T10:30:00+07:00",
  "author": {
    "@type": "Person",
    "name": "Bagas Saputra",
    "url": "https://www.example.com/author/bagas"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Jajan Digital",
    "logo": {
      "@type": "ImageObject",
      "url": "https://www.example.com/logo.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://www.example.com/buku/panduan-minion"
  }
}
</script>
```

---

## 3. Product & Offer (E-Commerce)

Enables pricing, stock status, and review ratings in SERP:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": "Shimano Acera RD-M3020-SGS",
  "image": [
    "https://www.example.com/images/rd-m3020-1.jpg"
  ],
  "description": "Rear Derailleur 7/8 Speed SGS long cage dengan kapasitas sproket hingga 40T.",
  "sku": "SHI-RDM3020-SGS",
  "mpn": "RDM3020SGS",
  "brand": {
    "@type": "Brand",
    "name": "Shimano"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://www.example.com/produk/shimano-acera-m3020",
    "priceCurrency": "IDR",
    "price": "314184",
    "priceValidUntil": "2027-12-31",
    "itemCondition": "https://schema.org/NewCondition",
    "availability": "https://schema.org/InStock"
  }
}
</script>
```

---

## 4. FAQPage (Collapsible Question Rich Snippet)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Berapa kapasitas maksimal sproket untuk Shimano Acera RD-M3020?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Shimano Acera RD-M3020 tipe SGS (Long Cage) dapat melayani sproket belakang hingga ukuran 40T."
      }
    },
    {
      "@type": "Question",
      "name": "Apakah rantai 8 speed cocok untuk gir 7 speed?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Ya, rantai 8 speed memiliki ketebalan internal yang sama (3/32 inci) dan kompatibel 100% untuk sistem transmisi 7 speed."
      }
    }
  ]
}
</script>
```

---

## 5. BreadcrumbList (Hierarchy Navigation)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Beranda",
      "item": "https://www.example.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Suku Cadang",
      "item": "https://www.example.com/parts"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Drivetrain",
      "item": "https://www.example.com/parts/drivetrain"
    }
  ]
}
</script>
```
