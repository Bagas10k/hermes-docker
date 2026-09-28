#!/usr/bin/env node
'use strict';

const MC = require('./mission-control');
const resolver = require('./skill-os-resolver');

async function main() {
  const [,, cmd, ...args] = process.argv;

  if (!cmd || cmd === 'status' || cmd === 'stat') {
    const summary = MC.getTelemetrySummary();
    console.log('\n================================================================');
    console.log('       HERMES V4 MISSION CONTROL & SKILL OS — TELEMETRY         ');
    console.log('================================================================');
    console.log('\n[MISI AKTIF]');
    summary.missions_by_status.forEach(m => console.log(`  • Status ${m.status}: ${m.count} misi`));
    
    console.log('\n[TUGAS / TASKS]');
    summary.tasks_by_status.forEach(t => console.log(`  • Status ${t.status}: ${t.count} tugas`));

    console.log(`\n[EVENT LOGS] : ${summary.total_events} peristiwa tercatat`);
    console.log(`[ARTEFAK]    : ${summary.total_artifacts} berkas terdaftar`);

    console.log('\n[ARMADA AGENT]');
    summary.active_fleet.forEach(a => {
      console.log(`  • [${a.division}] ${a.agent_id} (${a.status}) — ${a.role_description}`);
    });
    console.log('\n================================================================\n');
  } else if (cmd === 'resolve') {
    const query = args.join(' ');
    if (!query) {
      console.error('Masukkan query: mission-control resolve "<intent>"');
      process.exit(1);
    }
    const res = resolver.rankSkills(query);
    console.log('\n[SKILL OS RESOLUTION RESULT]');
    console.log(JSON.stringify(res, null, 2), '\n');
  } else if (cmd === 'sweep') {
    const zombies = MC.sweepZombieTasks();
    console.log(`[SWEEP] ${zombies.length} task zombie/expired berhasil dibersihkan.`);
  } else if (cmd === 'eval' || cmd === 'learn') {
    const learner = require('./eval-bayesian-learner');
    const subCmd = args[0];
    if (subCmd === 'compact') {
      const res = learner.compactStore();
      console.log('[BAYESIAN COMPACT]', JSON.stringify(res, null, 2));
    } else if (subCmd && subCmd.includes(':')) {
      const keyMap = {
        'grid': 'ui.layout.grid_container',
        'struktur': 'ui.layout.anti_ai_slop_structure',
        'anim': 'ui.motion.spring_physics',
        'copy': 'copy.b2b.architect_voice',
        'smooth': 'ui.motion.tactile_smoothness'
      };
      const batch = subCmd.split(',').filter(Boolean).map(p => {
        const [k, v] = p.split(':');
        return {
          canonical_key: keyMap[k.trim()] || `custom.${k.trim()}`,
          score: parseFloat(v.trim()),
          verdict: `Input via mission-control CLI: skor ${v.trim()}/10`
        };
      });
      const res = learner.ingestEvaluation(batch);
      console.log('[BAYESIAN EVALUATION & PRIORITIZED QUEUE]');
      console.log(JSON.stringify(res, null, 2));
    } else {
      const store = learner.loadStore();
      console.log('\n================================================================');
      console.log('       HERMES V4 BAYESIAN KNOWLEDGE STORE & BELIEF MATRIX        ');
      console.log('================================================================\n');
      console.log(`Versi Master : ${store.version}`);
      console.log(`Terakhir Update : ${store.last_updated}`);
      console.log(`Total Nodes  : ${Object.keys(store.knowledge_nodes).length}\n`);
      for (const [key, node] of Object.entries(store.knowledge_nodes)) {
        console.log(`• [${node.version}] ${key}`);
        console.log(`  Skor: ${node.latest_score}/10 | Prob: ${(node.posterior_probability * 100).toFixed(1)}% | Status: ${node.latest_score < 5 ? 'MUTATED_HARD_GATE' : 'ACCEPTABLE'}`);
        if (node.active_solutions.length > 0) {
          console.log(`  Solusi Aktif : ${node.active_solutions[0]}`);
        }
        if (node.deprecated_patterns.length > 0) {
          console.log(`  Pantangan   : ${node.deprecated_patterns.join('; ')}`);
        }
        console.log('');
      }
    }
  } else {
    console.log('Perintah: mission-control [status | resolve "<intent>" | sweep | eval "<scores>" | eval compact]');
  }
}

main().catch(err => {
  console.error('[FATAL]', err.message);
  process.exit(1);
});
