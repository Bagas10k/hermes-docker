# Voice, Tone, Bahasa Indonesia, and Localization

## Contents
1. Voice versus tone
2. Tone matrix
3. Bahasa Indonesia UI writing
4. English UI writing
5. Terminology systems
6. Localization expansion
7. Cultural and inclusive language

## 1. Voice versus tone

Voice is stable product personality.
Tone adapts to situation, severity, and emotional context.

Define voice with useful dimensions, for example:
- direct vs expressive
- formal vs conversational
- technical vs plain-language
- restrained vs playful

Avoid generic brand attributes such as "friendly, modern, professional" unless each is translated into observable writing rules.

## 2. Tone matrix

### Normal task
Clear, efficient, neutral-positive.

### Onboarding
Encouraging, low-pressure, informative.

### Success
Brief and confident.

### User-correctable error
Calm, specific, action-oriented.

### System failure
Transparent, accountable, helpful.

### Destructive action
Serious, precise, consequence-focused.

### Security or privacy
Direct, factual, non-sensational.

## 3. Bahasa Indonesia UI writing

Write naturally for Indonesian users rather than translating English word-for-word.

Prefer familiar, concise phrases:
- Simpan perubahan
- Tambah anggota
- Hapus proyek
- Coba lagi
- Lihat laporan
- Belum ada data

Choose pronouns based on product voice. "Anda" is common for formal/professional products. "Kamu" can work for consumer products with a conversational voice. Do not mix them randomly.

Avoid bureaucratic constructions when a shorter familiar phrase works.

Example:
Stiff: "Silakan melakukan pengisian alamat email Anda."
Natural: "Masukkan alamat email Anda."

Prefer consistent nouns. If using "proyek", do not switch to "project" unless the product intentionally uses English terminology.

English technical terms can remain when they are more familiar to the target users, but establish a glossary.

## 4. English UI writing

Use sentence case by default unless brand/system rules specify otherwise.

Prefer verbs that match the exact action. Avoid corporate filler such as "leverage", "utilize", and "synergize" when simple words are clearer.

## 5. Terminology systems

Maintain a product lexicon:

| Concept | Preferred term | Avoid | Notes |
| --- | --- | --- | --- |
| Work container | Workspace | Hub, space, team area | Use everywhere |
| User invitation | Invite | Add access | Verb and noun rules |

Update the lexicon when product concepts change.

## 6. Localization expansion

Design copy for translation:
- avoid fixed-width buttons that barely fit English
- avoid concatenating sentence fragments in code
- support pluralization correctly
- avoid embedded text in images
- allow labels to wrap when necessary
- test long translations
- account for right-to-left layouts when supported

Do not shorten source copy merely to force every translation into the same fixed container. Fix the layout when possible.

## 7. Cultural and inclusive language

Use respectful language. Avoid unnecessary assumptions about gender, family structure, ability, geography, or identity.

Be especially careful with humor in errors, financial flows, health, safety, security, and loss.
