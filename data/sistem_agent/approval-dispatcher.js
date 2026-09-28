#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const http = require('http');

const QUEUE_FILE = '/home/ubuntu/otak-koding/SISTEM_AGENT/APPROVAL_QUEUE.json';
const CONSTRAINTS_FILE = '/home/ubuntu/otak-koding/SISTEM_AGENT/NEGATIVE_CONSTRAINTS.json';

function loadQueue() {
  if (!fs.existsSync(QUEUE_FILE)) {
    return { schema_version: '1.0', items: [], updated_at: new Date().toISOString() };
  }
  try {
    return JSON.parse(fs.readFileSync(QUEUE_FILE, 'utf8'));
  } catch (e) {
    return { schema_version: '1.0', items: [], error: e.message };
  }
}

function saveQueue(queue) {
  queue.updated_at = new Date().toISOString();
  fs.writeFileSync(QUEUE_FILE, JSON.stringify(queue, null, 2), 'utf8');
}

async function listPending() {
  const queue = loadQueue();
  const pending = (queue.items || []).filter(i => i.status === 'PENDING_APPROVAL');
  console.log(`\n================================================================`);
  console.log(`  APPROVAL QUEUE — DRAF KONTEN MENUNGGU PERSETUJUAN MAS BAGAS   `);
  console.log(`================================================================`);
  if (pending.length === 0) {
    console.log('Tidak ada draf yang menunggu approval saat ini. Sistem steril.\n');
    return;
  }

  pending.forEach((item, idx) => {
    console.log(`\n[${idx + 1}] ID: ${item.id}`);
    console.log(`    Domain   : ${item.domain.toUpperCase()}`);
    console.log(`    Draft ID : ${item.draft_id}`);
    console.log(`    Judul    : ${item.headline}`);
    console.log(`    QC Skor  : ${item.qc_score || 'N/A'}/100`);
    console.log(`    Preview  : ${item.preview_url || 'Lokal'}`);
    console.log(`    Dibuat   : ${item.created_at}`);
  });
  console.log(`\nPerintah eksekusi:`);
  console.log(`  node approval-dispatcher.js approve <id>`);
  console.log(`  node approval-dispatcher.js reject <id> [alasan]\n`);
}

function findItem(queue, targetId) {
  const clean = String(targetId).trim();
  return (queue.items || []).find(i => 
    i.id === clean || 
    i.draft_id === clean || 
    i.id.startsWith(clean) || 
    clean.startsWith(i.id) ||
    clean.includes(i.draft_id) ||
    (i.draft_id && clean.endsWith(i.draft_id))
  );
}

async function approveItem(targetId) {
  const queue = loadQueue();
  const item = findItem(queue, targetId);

  if (!item) {
    console.error(`[ERROR] Draf dengan ID "${targetId}" tidak ditemukan di antrean.`);
    process.exit(1);
  }

  if (item.status !== 'PENDING_APPROVAL') {
    console.log(`[INFO] Item ${item.id} sudah berstatus: ${item.status}.`);
    return;
  }

  console.log(`[APPROVE] Memproses publikasi resmi untuk ${item.domain}: "${item.headline}"...`);

  if (item.domain === 'sputarai') {
    const adminHeaders = {
      'x-admin-pin': 'cihuy2026',
      'Origin': 'https://www.jajandigital.web.id'
    };

    // 1. Approve di Express API
    const approveRes = await fetch(`http://127.0.0.1:3050/api/admin/publications/${item.publication_id}/approve`, {
      method: 'POST',
      headers: adminHeaders
    });
    const approveJson = await approveRes.json();
    if (!approveJson.ok) throw new Error(`Approve API gagal: ${approveJson.error}`);

    // 2. Publish ke Instagram via Meta Graph API
    const pubRes = await fetch(`http://127.0.0.1:3050/api/admin/publications/${item.publication_id}/publish`, {
      method: 'POST',
      headers: adminHeaders
    });
    const pubJson = await pubRes.json();
    if (!pubJson.ok) throw new Error(`Publish API gagal: ${pubJson.error}`);

    item.status = 'APPROVED_AND_PUBLISHED';
    item.published_id = pubJson.published_id;
    item.approved_by = 'Mas Bagas Saputra';
    item.approved_at = new Date().toISOString();
    saveQueue(queue);

    console.log(`[SUKSES] @sputarai berhasil terbit! IG Media ID: ${pubJson.published_id}`);

    // Notifikasi sukses ke Telegram
    try {
      const { sendTelegramPostNotification } = require('/home/ubuntu/penelitian-pola-pikir-ai/scripts/telegram-notifier');
      await sendTelegramPostNotification({
        title: item.headline,
        publisher: item.source || 'The Global AI Chronicle',
        permalink: `https://www.instagram.com/sputarai/`,
        type: 'CAROUSEL'
      });
    } catch (e) {}
  } else if (item.domain === 'sputarball') {
    const { publishDraftToInstagram, notifyTelegram } = require('/home/ubuntu/sputarball/scripts/publisher');
    const pubResult = await publishDraftToInstagram(item.draft_id, { force: true });

    if (pubResult.mode === 'STAGING_READY' || !pubResult.ig_media_id) {
      throw new Error(`Publikasi gagal atau tertahan di staging: ${pubResult.message || 'Kredensial IG belum siap'}`);
    }

    item.status = 'APPROVED_AND_PUBLISHED';
    item.published_id = pubResult.ig_media_id;
    item.permalink = pubResult.permalink;
    item.approved_by = 'Mas Bagas Saputra';
    item.approved_at = new Date().toISOString();
    saveQueue(queue);

    console.log(`[SUKSES] @sputarball berhasil terbit! Permalink: ${pubResult.permalink}`);

    // Notifikasi sukses ke Telegram BAgent
    try {
      await notifyTelegram({
        headline: item.headline,
        source: item.source || 'The Guardian Football',
        permalink: pubResult.permalink,
        tiktokPermalink: pubResult.tiktok?.permalink || (pubResult.tiktok?.status ? 'https://www.tiktok.com/@sputarball' : null),
        tiktokStatus: pubResult.tiktok?.status || 'PUBLISHED',
        draftId: item.draft_id
      });
    } catch (e) {}
  } else {
    throw new Error(`Domain ${item.domain} tidak didukung`);
  }
}

async function rejectItem(targetId, reason) {
  const queue = loadQueue();
  const item = findItem(queue, targetId);

  if (!item) {
    console.error(`[ERROR] Draf dengan ID "${targetId}" tidak ditemukan.`);
    process.exit(1);
  }

  item.status = 'REJECTED';
  item.rejected_by = 'Mas Bagas Saputra';
  item.rejected_reason = reason || 'Tidak disetujui Mas Bagas';
  item.rejected_at = new Date().toISOString();
  saveQueue(queue);

  console.log(`[REJECTED] Draf ${item.id} ditolak. Status dicatat ke antrean.`);
}

async function main() {
  const [,, cmd, id, ...rest] = process.argv;
  if (!cmd || cmd === 'list' || cmd === 'ls') {
    await listPending();
  } else if (cmd === 'approve') {
    if (!id) {
      console.error('Harap masukkan ID draf: node approval-dispatcher.js approve <id>');
      process.exit(1);
    }
    await approveItem(id);
  } else if (cmd === 'reject') {
    if (!id) {
      console.error('Harap masukkan ID draf: node approval-dispatcher.js reject <id> [alasan]');
      process.exit(1);
    }
    await rejectItem(id, rest.join(' '));
  } else {
    console.log('Perintah tersedia: list | approve <id> | reject <id> [alasan]');
  }
}

main().catch(err => {
  console.error('[FATAL]', err.message);
  process.exit(1);
});
