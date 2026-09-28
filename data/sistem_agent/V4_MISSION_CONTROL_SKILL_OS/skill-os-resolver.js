'use strict';

/**
 * SKILL OS RESOLVER — V4 SHADOW ENGINE
 * Menyelesaikan pencocokan skill berbasis metadata intent, pemeriksaan NO_SKILL,
 * deteksi konflik, dan lazy-loading tanpa membebani context window model.
 */

const fs = require('fs');
const path = require('path');

const REGISTRY_PATH = path.join(__dirname, 'skills_registry.json');

let _registryCache = null;
function getRegistry() {
  if (!_registryCache) {
    if (fs.existsSync(REGISTRY_PATH)) {
      _registryCache = JSON.parse(fs.readFileSync(REGISTRY_PATH, 'utf8')).skills || [];
    } else {
      _registryCache = [];
    }
  }
  return _registryCache;
}

// 1. Pemeriksaan NO_SKILL: Deteksi tugas sederhana yang tidak butuh beban skill
const TRIVIAL_PATTERNS = [
  /^(cek|lihat|status|list|ls|ps|pm2 list|git status)/i,
  /^(edit typo|perbaiki ejaan|ganti kata|ubah 1 baris)/i,
  /^(cat|read|tail|head|grep)/i,
  /^(ping|curl|cek port)/i
];

function checkNoSkill(intent) {
  const clean = intent.trim().toLowerCase();
  if (clean.length < 40 && TRIVIAL_PATTERNS.some(p => p.test(clean))) {
    return {
      decision: 'NO_SKILL',
      reason: 'Tugas dasar dapat dieksekusi langsung oleh kapabilitas inti LLM / tools standar tanpa token overhead skill.'
    };
  }
  return null;
}

// 2. Pencocokan & Pemeringkatan Metadata (Skill Ranking)
function rankSkills(intent) {
  const noSkill = checkNoSkill(intent);
  if (noSkill) return noSkill;

  const registry = getRegistry();
  const tokens = intent.toLowerCase().replace(/[^a-z0-9_-]/g, ' ').split(/\s+/).filter(t => t.length >= 3);

  const scored = [];

  for (const skill of registry) {
    let score = 0;
    const nameLower = skill.name.toLowerCase();
    const descLower = skill.description.toLowerCase();

    for (const t of tokens) {
      if (nameLower.includes(t)) score += 5;
      if (skill.keywords && skill.keywords.includes(t)) score += 3;
      if (descLower.includes(t)) score += 1;
    }

    if (score > 0) {
      let confidence = 'WEAK_MATCH';
      if (score >= 12) confidence = 'STRONG_MATCH';
      else if (score >= 6) confidence = 'GOOD_MATCH';

      scored.push({
        skill_id: skill.skill_id,
        name: skill.name,
        category: skill.category,
        version: skill.version,
        score,
        confidence,
        path: skill.path,
        use_count: skill.use_count
      });
    }
  }

  scored.sort((a, b) => b.score - a.score || b.use_count - a.use_count);

  if (scored.length === 0) {
    return {
      decision: 'NO_SKILL',
      reason: 'Tidak ada skill spesifik yang cocok; menggunakan kapabilitas dasar model.'
    };
  }

  const primary = scored[0];

  // 3. Resolusi Konflik & Pembentukan Rantai (Skill Chain)
  const chain = [primary.name];
  if (intent.includes('landing') || intent.includes('desain') || intent.includes('web')) {
    if (!chain.includes('design-md')) chain.unshift('design-md');
    if (!chain.includes('impeccable')) chain.push('impeccable');
  }

  return {
    decision: 'SKILL_RESOLVED',
    primary_skill: primary,
    candidates: scored.slice(0, 4),
    suggested_chain: chain
  };
}

// 4. Lazy Loader: Memuat isi penuh SKILL.md HANYA jika dipanggil
function lazyLoadSkill(skillId) {
  const registry = getRegistry();
  const target = registry.find(s => s.skill_id === skillId || s.name === skillId);
  if (!target || !fs.existsSync(target.path)) {
    throw new Error(`Skill '${skillId}' tidak ditemukan di registry lokal.`);
  }
  return {
    skill_id: target.skill_id,
    version: target.version,
    path: target.path,
    content: fs.readFileSync(target.path, 'utf8')
  };
}

module.exports = {
  getRegistry,
  checkNoSkill,
  rankSkills,
  lazyLoadSkill
};
