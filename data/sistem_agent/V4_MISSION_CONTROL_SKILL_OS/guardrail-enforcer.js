'use strict';

/**
 * GUARDRAIL ENFORCER — V4 PHASE 4 / S4
 * Menegakkan aturan negatif dan batasan izin sebelum tool eksekusi dipanggil.
 * Merujuk langsung ke NEGATIVE_CONSTRAINTS.json.
 */

const fs = require('fs');
const path = require('path');
const MC = require('./mission-control');

const CONSTRAINTS_PATH = '/home/ubuntu/otak-koding/SISTEM_AGENT/NEGATIVE_CONSTRAINTS.json';

class GuardrailEnforcer {
  static loadConstraints() {
    if (!fs.existsSync(CONSTRAINTS_PATH)) {
      throw new Error(`File batasan ${CONSTRAINTS_PATH} tidak ditemukan.`);
    }
    return JSON.parse(fs.readFileSync(CONSTRAINTS_PATH, 'utf8'));
  }

  /**
   * Validasi apakah sebuah aksi diizinkan atau wajib diblokir
   */
  static validateAction(domain, actionName, payload = {}, traceId = null) {
    const config = this.loadConstraints();
    const policy = config.approval_policy || {};
    const blockedActions = policy.blocked_auto_actions || [];

    // 1. Cek aksi yang diblokir mutlak dari eksekusi otomatis
    if (blockedActions.includes(actionName)) {
      const violation = {
        allowed: false,
        action: actionName,
        domain: domain,
        severity: 'HARD_VETO',
        reason: `Aksi '${actionName}' dilarang oleh guardrail kebijakan (blocked_auto_actions).`
      };

      if (traceId) {
        MC.logEvent(traceId, null, null, 'GUARDRAIL_VETO', violation);
      }

      return violation;
    }

    // 1b. Cek publikasi tanpa kelulusan QC
    if ((actionName === 'instagram_media_publish' || actionName === 'tiktok_publish') && payload.qc_score !== undefined && payload.qc_score < (policy.qc_passing_threshold || 80)) {
      const violation = {
        allowed: false,
        action: actionName,
        domain: domain,
        severity: 'HARD_VETO',
        reason: `Draf ditolak QC: skor (${payload.qc_score}) di bawah ambang batas minimal (${policy.qc_passing_threshold || 80}). Publikasi dibatalkan.`
      };
      if (traceId) MC.logEvent(traceId, null, null, 'GUARDRAIL_VETO', violation);
      return violation;
    }

    // 2. Cek larangan localhost publik pada payload web
    if (domain === 'web' && payload.html && /127\.0\.0\.1|localhost/i.test(payload.html)) {
      const violation = {
        allowed: false,
        action: actionName,
        domain: domain,
        severity: 'HARD_VETO',
        reason: 'Haram menyertakan localhost atau 127.0.0.1 dalam konten HTML publik.'
      };
      if (traceId) MC.logEvent(traceId, null, null, 'GUARDRAIL_VETO', violation);
      return violation;
    }

    // 3. Cek larangan template lapangan generik pada payload sepak bola
    if (domain === 'sputarball' && payload.image_url && /stadium_epic|football_goal/i.test(payload.image_url)) {
      const violation = {
        allowed: false,
        action: actionName,
        domain: domain,
        severity: 'HARD_VETO',
        reason: 'Haram menggunakan gambar gawang/lapangan hijau 3D generik. Wajib foto asli aksi pemain HD.'
      };
      if (traceId) MC.logEvent(traceId, null, null, 'GUARDRAIL_VETO', violation);
      return violation;
    }

    return { allowed: true, action: actionName, domain: domain };
  }
}

module.exports = GuardrailEnforcer;
