'use strict';

/**
 * MISSION CONTROL ENGINE — HERMES V4 ORCHESTRATION LAYER
 * Mengelola pendaftaran misi, pelacakan tugas, distributed lease/heartbeat,
 * serta pencatatan audit log terstruktur.
 */

const { DatabaseSync } = require('node:sqlite');
const path = require('path');
const crypto = require('crypto');
const resolver = require('./skill-os-resolver');

const DB_PATH = path.join(__dirname, 'mission_control.sqlite');
const db = new DatabaseSync(DB_PATH);
db.exec('PRAGMA journal_mode = WAL;');
db.exec('PRAGMA busy_timeout = 5000;');
db.exec('PRAGMA synchronous = NORMAL;');
db.exec('PRAGMA foreign_keys = ON;');

function generateTraceId() {
  return 'trc_' + crypto.randomBytes(8).toString('hex');
}

function generateId(prefix = 'mis') {
  return `${prefix}_` + crypto.randomBytes(6).toString('hex');
}

class MissionControl {
  /**
   * Buat misi baru dengan klasifikasi kompleksitas dan pencocokan Skill OS otomatis
   */
  static createMission(intent, options = {}) {
    const traceId = options.traceId || generateTraceId();
    const missionId = generateId('mis');
    const title = options.title || intent.slice(0, 80);

    // 1. Konsultasi ke Skill OS Resolver
    const resolution = resolver.rankSkills(intent);
    let complexity = 'STANDARD';
    let assignedSkill = null;
    let suggestedChain = [];

    if (resolution.decision === 'NO_SKILL') {
      complexity = 'FAST';
    } else if (resolution.suggested_chain && resolution.suggested_chain.length > 2) {
      complexity = 'DEEP';
      suggestedChain = resolution.suggested_chain;
      assignedSkill = resolution.primary_skill.name;
    } else {
      complexity = 'STANDARD';
      assignedSkill = resolution.primary_skill.name;
      suggestedChain = resolution.suggested_chain || [assignedSkill];
    }

    // 2. Simpan Misi ke Database
    db.prepare(`
      INSERT INTO missions (id, title, intent, complexity, division, status, trace_id)
      VALUES (?, ?, ?, ?, ?, 'RUNNING', ?)
    `).run(missionId, title, intent, complexity, options.division || 'GENERAL', traceId);

    // 3. Catat Event Log
    this.logEvent(traceId, missionId, null, 'MISSION_CREATED', {
      title,
      complexity,
      skill_decision: resolution.decision,
      assigned_skill: assignedSkill,
      suggested_chain: suggestedChain
    });

    return {
      mission_id: missionId,
      trace_id: traceId,
      title,
      complexity,
      skill_decision: resolution.decision,
      primary_skill: assignedSkill,
      suggested_chain: suggestedChain
    };
  }

  /**
   * Alokasikan sub-task dengan lease waktu (mencegah task zombie/hang)
   */
  static assignTask(missionId, title, agentId, skillUsed = null, leaseSeconds = 300) {
    const taskId = generateId('tsk');
    const now = Date.now();
    const leaseExpires = new Date(now + leaseSeconds * 1000).toISOString();

    db.prepare(`
      INSERT INTO tasks (id, mission_id, title, agent_id, skill_used, status, lease_expires_at, last_heartbeat_at)
      VALUES (?, ?, ?, ?, ?, 'RUNNING', ?, CURRENT_TIMESTAMP)
    `).run(taskId, missionId, title, agentId, skillUsed, leaseExpires);

    const mission = db.prepare('SELECT trace_id FROM missions WHERE id = ?').get(missionId);
    if (mission) {
      this.logEvent(mission.trace_id, missionId, taskId, 'TASK_STARTED', {
        title,
        agent_id: agentId,
        skill_used: skillUsed,
        lease_seconds: leaseSeconds
      });
    }

    return { task_id: taskId, lease_expires_at: leaseExpires };
  }

  /**
   * Perbarui heartbeat tugas untuk memperpanjang lease
   */
  static heartbeat(taskId, extendSeconds = 300) {
    const now = Date.now();
    const leaseExpires = new Date(now + extendSeconds * 1000).toISOString();
    const res = db.prepare(`
      UPDATE tasks 
      SET last_heartbeat_at = CURRENT_TIMESTAMP, lease_expires_at = ?
      WHERE id = ? AND status = 'RUNNING'
    `).run(leaseExpires, taskId);

    return res.changes > 0;
  }

  /**
   * Selesaikan tugas dan catat artefak luaran
   */
  static completeTask(taskId, resultArtifact = null) {
    const res = db.prepare(`
      UPDATE tasks 
      SET status = 'COMPLETED', result_artifact = ?, completed_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `).run(resultArtifact, taskId);

    const task = db.prepare('SELECT mission_id, title FROM tasks WHERE id = ?').get(taskId);
    if (task) {
      const mission = db.prepare('SELECT trace_id FROM missions WHERE id = ?').get(task.mission_id);
      if (mission) {
        this.logEvent(mission.trace_id, task.mission_id, taskId, 'TASK_COMPLETED', {
          title: task.title,
          artifact: resultArtifact
        });
      }
    }

    return res.changes > 0;
  }

  /**
   * Selesaikan seluruh misi
   */
  static completeMission(missionId, status = 'COMPLETED') {
    const res = db.prepare(`
      UPDATE missions 
      SET status = ?, completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `).run(status, missionId);

    const mission = db.prepare('SELECT trace_id, title FROM missions WHERE id = ?').get(missionId);
    if (mission) {
      this.logEvent(mission.trace_id, missionId, null, 'MISSION_COMPLETED', {
        title: mission.title,
        final_status: status
      });
    }

    return res.changes > 0;
  }

  /**
   * Rekam artefak baru ke dalam registry
   */
  static recordArtifact(missionId, taskId, name, filePath, type = 'CODE', contentHash = null) {
    const artifactId = generateId('art');
    db.prepare(`
      INSERT INTO artifacts (id, mission_id, task_id, name, path, artifact_type, content_hash)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `).run(artifactId, missionId, taskId, name, filePath, type, contentHash);

    return artifactId;
  }

  /**
   * Deteksi dan amankan task zombie yang habis masa lease-nya
   */
  static sweepZombieTasks() {
    const zombies = db.prepare(`
      SELECT id, mission_id, title, agent_id 
      FROM tasks 
      WHERE status = 'RUNNING' AND lease_expires_at < datetime('now')
    `).all();

    for (const z of zombies) {
      db.prepare(`
        UPDATE tasks 
        SET status = 'TIMED_OUT', error_message = 'Lease expired without heartbeat renewal'
        WHERE id = ?
      `).run(z.id);

      const mission = db.prepare('SELECT trace_id FROM missions WHERE id = ?').get(z.mission_id);
      if (mission) {
        this.logEvent(mission.trace_id, z.mission_id, z.id, 'TASK_TIMED_OUT', {
          title: z.title,
          agent_id: z.agent_id
        });
      }
    }

    return zombies;
  }

  /**
   * Tulis structured event envelope
   */
  static logEvent(traceId, missionId, taskId, eventType, payload = {}) {
    db.prepare(`
      INSERT INTO event_logs (trace_id, mission_id, task_id, event_type, payload_json)
      VALUES (?, ?, ?, ?, ?)
    `).run(traceId, missionId, taskId, eventType, JSON.stringify(payload));
  }

  /**
   * Ringkasan telemetri status Mission Control
   */
  static getTelemetrySummary() {
    const missions = db.prepare('SELECT status, COUNT(*) as count FROM missions GROUP BY status').all();
    const tasks = db.prepare('SELECT status, COUNT(*) as count FROM tasks GROUP BY status').all();
    const eventsCount = db.prepare('SELECT COUNT(*) as total FROM event_logs').get().total;
    const artifactsCount = db.prepare('SELECT COUNT(*) as total FROM artifacts').get().total;
    const agents = db.prepare('SELECT agent_id, division, status, role_description FROM agent_registry').all();

    return {
      missions_by_status: missions,
      tasks_by_status: tasks,
      total_events: eventsCount,
      total_artifacts: artifactsCount,
      active_fleet: agents
    };
  }
}

module.exports = MissionControl;
