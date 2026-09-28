#!/usr/bin/env node
/**
 * eval-bayesian-learner.js
 * Bayesian Evaluation & Knowledge Morphing Engine (V4 Mission Control Core)
 *
 * Pencipta: Bagas Saputra (Bagas Cihuy) & Hermes Agent
 * Doktrin: Value-Based Bayesian Reinforcement + Semantic Knowledge Morphing
 *
 * Menerapkan:
 * 1. Bayesian Belief Updating: P(Pattern Good | Score History)
 * 2. Prioritas Deviasi Terbesar: Delta = (10 - score) * weight (Amdahl bottleneck first)
 * 3. Semantic Morphing: Upsert berbasis Canonical Key tanpa duplikasi data.
 */

const fs = require('fs');
const path = require('path');

const STORE_PATH = path.join(__dirname, '../BAYESIAN_KNOWLEDGE_STORE.json');

// Bobot Kategori untuk Prioritas Eksekusi (Structural > Motion > Cosmetics)
const CATEGORY_WEIGHTS = {
  'layout': 1.5,      // Arsitektur bento, grid, struktur data (Kritis)
  'architecture': 1.5,
  'security': 1.5,
  'copywriting': 1.2, // Pesan teknis, kejelasan proposisi B2B
  'motion': 1.0,      // Animasi pegas, timing, transisi
  'tactile': 1.0,     // Responsivitas klik, haptic, audio
  'cosmetics': 0.8    // Warna aksen, border halus, bayangan
};

// Inisialisasi atau Baca Store
function loadStore() {
  if (!fs.existsSync(STORE_PATH)) {
    const initial = {
      version: '1.0.0',
      last_updated: new Date().toISOString(),
      knowledge_nodes: {},
      eval_history: []
    };
    fs.writeFileSync(STORE_PATH, JSON.stringify(initial, null, 2), 'utf-8');
    return initial;
  }
  try {
    return JSON.parse(fs.readFileSync(STORE_PATH, 'utf-8'));
  } catch (err) {
    console.error('Error reading knowledge store, fallback to empty:', err.message);
    return { version: '1.0.0', last_updated: new Date().toISOString(), knowledge_nodes: {}, eval_history: [] };
  }
}

function saveStore(store) {
  store.last_updated = new Date().toISOString();
  fs.writeFileSync(STORE_PATH, JSON.stringify(store, null, 2), 'utf-8');
}

// Ingest Evaluasi Nilai dari Mas Bagas
function ingestEvaluation(evaluationBatch) {
  const store = loadStore();
  const results = [];
  const evalId = 'eval_' + Date.now().toString(16);

  // 1. Hitung Prioritas Deviasi Terbesar
  const prioritizedQueue = evaluationBatch.map(item => {
    const category = item.canonical_key.split('.')[1] || 'cosmetics';
    const weight = CATEGORY_WEIGHTS[category] || 1.0;
    const deficit = (10 - item.score);
    const priorityScore = parseFloat((deficit * weight).toFixed(2));

    return {
      ...item,
      category,
      weight,
      deficit,
      priorityScore
    };
  }).sort((a, b) => b.priorityScore - a.priorityScore);

  // 2. Bayesian Belief Updating & Semantic Morphing per Node
  for (const item of prioritizedQueue) {
    const key = item.canonical_key;
    let node = store.knowledge_nodes[key];

    const normalizedScore = item.score / 10; // Skala 0.0 - 1.0

    if (!node) {
      // Entri Baru (v1.0)
      node = {
        canonical_key: key,
        version: '1.0.0',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        observations_count: 1,
        prior_probability: 0.50,
        posterior_probability: parseFloat((0.4 * 0.50 + 0.6 * normalizedScore).toFixed(4)),
        latest_score: item.score,
        latest_verdict: item.verdict || 'Initial evaluation',
        active_solutions: item.proven_solution ? [item.proven_solution] : [],
        deprecated_patterns: item.score < 5 && item.failed_pattern ? [item.failed_pattern] : []
      };
    } else {
      // Mutasi Data yang Sudah Ada (v1.x -> v2.x) — Anti Timpa Duplikat!
      const prevVerParts = node.version.split('.').map(Number);
      const isMajor = item.score < 5; // Skor hancur memicu mutasi mayor
      const newVersion = isMajor 
        ? `${prevVerParts[0] + 1}.0.0` 
        : `${prevVerParts[0]}.${prevVerParts[1] + 1}.0`;

      // Bayesian Belief Update (Exponential moving update)
      const currentPrior = node.posterior_probability;
      const alpha = 0.35; // Bobot ke data riwayat sebelumnya
      const newPosterior = parseFloat((alpha * currentPrior + (1 - alpha) * normalizedScore).toFixed(4));

      // Deprecate pola gagal jika ada
      if (item.failed_pattern && !node.deprecated_patterns.includes(item.failed_pattern)) {
        node.deprecated_patterns.push(item.failed_pattern);
      }

      // Terapkan data baru / perbaiki solusi aktif (hilangkan solusi lama jika bertentangan)
      if (item.proven_solution) {
        // Hilangkan solusi lama yang usang agar tidak dobel
        node.active_solutions = [item.proven_solution];
      }

      node.version = newVersion;
      node.updated_at = new Date().toISOString();
      node.observations_count += 1;
      node.prior_probability = currentPrior;
      node.posterior_probability = newPosterior;
      node.latest_score = item.score;
      node.latest_verdict = item.verdict || node.latest_verdict;
    }

    store.knowledge_nodes[key] = node;
    results.push({
      key,
      version: node.version,
      priorityRank: item.priorityScore,
      posteriorProb: node.posterior_probability,
      status: item.score < 5 ? 'CRITICAL_MUTATION_REQUIRED' : 'ACCEPTABLE'
    });
  }

  // Rekam riwayat evaluasi ringkas
  store.eval_history.unshift({
    eval_id: evalId,
    timestamp: new Date().toISOString(),
    items: evaluationBatch.map(i => ({ key: i.canonical_key, score: i.score }))
  });

  // Batasi riwayat evaluasi max 50 entri agar tidak bengkak
  if (store.eval_history.length > 50) {
    store.eval_history = store.eval_history.slice(0, 50);
  }

  saveStore(store);
  return {
    evalId,
    prioritizedExecutionQueue: prioritizedQueue,
    updatedNodes: results
  };
}

// Compact & Deduplikasi Data
function compactStore() {
  const store = loadStore();
  let mergedCount = 0;
  let prunedCount = 0;

  const keys = Object.keys(store.knowledge_nodes);
  for (const key of keys) {
    const node = store.knowledge_nodes[key];
    
    // Prune duplikasi di active_solutions
    const uniqueSolutions = [...new Set(node.active_solutions)];
    if (uniqueSolutions.length !== node.active_solutions.length) {
      prunedCount += (node.active_solutions.length - uniqueSolutions.length);
      node.active_solutions = uniqueSolutions;
    }

    // Prune duplikasi di deprecated_patterns
    const uniqueDeprecated = [...new Set(node.deprecated_patterns)];
    if (uniqueDeprecated.length !== node.deprecated_patterns.length) {
      prunedCount += (node.deprecated_patterns.length - uniqueDeprecated.length);
      node.deprecated_patterns = uniqueDeprecated;
    }
  }

  saveStore(store);
  return {
    totalNodes: keys.length,
    prunedDuplicates: prunedCount,
    status: 'STORE_COMPACTED_ZERO_DUPLICATES'
  };
}

// CLI Handler
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0] || 'status';

  if (command === 'status') {
    const store = loadStore();
    console.log('=== BAYESIAN KNOWLEDGE STORE STATUS ===');
    console.log(`Versi: ${store.version}`);
    console.log(`Terakhir Diperbarui: ${store.last_updated}`);
    console.log(`Total Node Pengetahuan: ${Object.keys(store.knowledge_nodes).length}`);
    console.log(`Riwayat Evaluasi: ${store.eval_history.length}`);
    console.log('---------------------------------------');
    for (const [key, node] of Object.entries(store.knowledge_nodes)) {
      console.log(`[${node.version}] ${key}: Skor ${node.latest_score}/10 (Prob: ${(node.posterior_probability * 100).toFixed(1)}%)`);
      if (node.active_solutions.length > 0) {
        console.log(`   Solusi Aktif: ${node.active_solutions[0]}`);
      }
      if (node.deprecated_patterns.length > 0) {
        console.log(`   Pantangan Usang: ${node.deprecated_patterns.join(', ')}`);
      }
    }
  } else if (command === 'compact') {
    const res = compactStore();
    console.log('Hasil Pemadatan Data:', JSON.stringify(res, null, 2));
  } else if (command === 'eval') {
    // Contoh input: node eval-bayesian-learner.js eval "grid:2,anim:4,copy:5,smooth:6"
    const scoreStr = args[1] || '';
    const parts = scoreStr.split(',').filter(Boolean);
    const batch = [];

    const keyMap = {
      'grid': 'ui.layout.grid_container',
      'struktur': 'ui.layout.anti_ai_slop_structure',
      'anim': 'ui.motion.spring_physics',
      'copy': 'copy.b2b.architect_voice',
      'smooth': 'ui.motion.tactile_smoothness'
    };

    for (const p of parts) {
      const [k, v] = p.split(':');
      if (k && v) {
        const canonical = keyMap[k.trim()] || `custom.${k.trim()}`;
        const score = parseFloat(v.trim());
        batch.push({
          canonical_key: canonical,
          score: score,
          verdict: `Input via CLI: skor ${score}/10`
        });
      }
    }

    if (batch.length === 0) {
      console.log('Format: node eval-bayesian-learner.js eval "grid:2,anim:4,copy:5,smooth:6"');
      process.exit(1);
    }

    const res = ingestEvaluation(batch);
    console.log('Hasil Evaluasi Bayesian & Prioritas Eksekusi:');
    console.log(JSON.stringify(res, null, 2));
  } else {
    console.log('Perintah: status | eval "<scores>" | compact');
  }
}

module.exports = {
  loadStore,
  saveStore,
  ingestEvaluation,
  compactStore
};
