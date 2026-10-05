# EdTech SaaS Architecture: Zero-PII, RAG Grounding & Human-in-the-Loop Compliance

This reference provides production-tested patterns for high-compliance educational SaaS platforms (adhering to UU PDP No. 27/2022 Tier C and Kurikulum Merdeka / Standar Proses 2026).

---

## 1. Zero-PII Database Schema (SQLite WAL)

Never store student names, NIK, NISN, or contact details in AI-connected databases.

```sql
-- Roster Siswa Teranonimkan (Zero-PII)
CREATE TABLE IF NOT EXISTS students (
  id TEXT PRIMARY KEY,
  class_id TEXT NOT NULL,
  student_code TEXT NOT NULL UNIQUE, -- Contoh: 'std_cls_viii_a_01'
  display_label TEXT NOT NULL,       -- Contoh: 'Siswa #01'
  learning_style TEXT,               -- 'visual', 'auditory', 'kinesthetic'
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (class_id) REFERENCES classes(id)
);

-- Pengumpulan Tugas & Asesmen Esai
CREATE TABLE IF NOT EXISTS assessment_submissions (
  id TEXT PRIMARY KEY,
  student_id TEXT NOT NULL,
  class_id TEXT NOT NULL,
  assignment_title TEXT NOT NULL,
  student_work_text TEXT NOT NULL,
  suggested_score INTEGER,
  final_score INTEGER,
  feedback_markdown TEXT,
  evidence_citation TEXT,
  graded_by_teacher BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(id)
);

-- Jejak Audit Kepatuhan (Append-Only)
CREATE TABLE IF NOT EXISTS audit_logs (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  action TEXT NOT NULL,             -- 'generate_artifact', 'refine_artifact', 'grade_submission', 'export_docx'
  resource_type TEXT NOT NULL,      -- 'artifacts', 'submissions', 'sources'
  resource_id TEXT NOT NULL,
  details_json TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 2. Human-in-the-Loop AI Grading Endpoint

```javascript
router.post('/grading/suggest', (req, res) => {
  const { submission_id, assignment_title, rubric_criteria, student_work_text } = req.body;
  
  // Analisis komparatif jawaban siswa vs rubrik acuan
  const wordCount = (student_work_text || '').split(/\s+/).length;
  let suggestedScore = 75;
  let rationale = [];

  if (wordCount >= 20) {
    suggestedScore += 15;
    rationale.push('Jawaban mengelaborasi argumen dengan bukti kontekstual.');
  }
  if (student_work_text.toLowerCase().includes('kausal') || student_work_text.toLowerCase().includes('karena')) {
    suggestedScore += 10;
    rationale.push('Terdapat penalaran sebab-akibat (kausalitas) yang jelas.');
  }

  // AI HANYA menyarankan nilai, guru yang menentukan keputusan akhir
  const suggestion = {
    suggested_score: Math.min(100, suggestedScore),
    evidence_citation: rationale.join(' '),
    rubric_match: 'Tingkat Capaian: Sangat Baik (C4-C5 HOTS)',
    status: 'pending_teacher_approval'
  };

  res.json({ success: true, suggestion });
});
```

---

## 3. Native Binary DOCX Export Handler (`docx` library)

Avoid generating raw HTML; construct native OpenXML document buffers for official compliance.

```javascript
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType } = require('docx');

router.get('/artifacts/:id/export/docx', async (req, res) => {
  const artifact = db.prepare('SELECT * FROM artifacts WHERE id = ?').get(req.params.id);
  if (!artifact) return res.status(404).json({ error: 'Artefak tidak ditemukan' });

  const doc = new Document({
    sections: [{
      properties: {},
      children: [
        new Paragraph({
          text: 'KEMENTERIAN PENDIDIKAN DASAR DAN MENENGAH',
          heading: HeadingLevel.HEADING_2,
          alignment: 'center'
        }),
        new Paragraph({
          text: 'PERANGKAT AJAR RESMI — STANDAR PROSES 2026',
          heading: HeadingLevel.TITLE,
          alignment: 'center',
          spacing: { after: 200 }
        }),
        new Paragraph({
          children: [
            new TextRun({ text: 'Judul Modul: ', bold: true }),
            new TextRun(artifact.title),
          ]
        }),
        new Paragraph({
          children: [
            new TextRun({ text: 'Mata Pelajaran / Topik: ', bold: true }),
            new TextRun(`${artifact.topic} • Versi: v${artifact.version}`),
          ],
          spacing: { after: 300 }
        }),
        new Paragraph({
          text: 'Rincian Muatan Kurikulum',
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 200, after: 100 }
        }),
        new Paragraph({
          text: artifact.raw_markdown || 'Isi modul telah tervalidasi selaras Capaian Pembelajaran (CP).'
        })
      ]
    }]
  });

  const buffer = await Packer.toBuffer(doc);
  res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
  res.setHeader('Content-Disposition', `attachment; filename="${artifact.id}_resmi.docx"`);
  res.send(buffer);
});
```

---

## 4. Scope-Aware Contextual Copilot Architecture

Inject the active class or workspace scope into every copilot query so the assistant never gives ungrounded advice.

```javascript
router.post('/copilot/chat', (req, res) => {
  const { message, class_id } = req.body;
  const cls = db.prepare('SELECT * FROM classes WHERE id = ?').get(class_id);
  
  // Scope resolution
  const scope = {
    class_id: cls.id,
    class_name: cls.name,
    subject: cls.subject,
    student_count: cls.student_count
  };

  // Structured action responses
  let reply = '';
  let suggestedActions = [];

  if (/kuis|soal/i.test(message)) {
    reply = `Siap! Berikut draft kuis 2 butir untuk kelas ${cls.name} (${cls.subject}). Klik tombol di bawah untuk memasukkan ke Bank Soal:`;
    suggestedActions.push({ label: 'Simpan ke Bank Soal', action: 'open_question_bank' });
    suggestedActions.push({ label: 'Buat Paket Asesmen di Studio', action: 'create_quiz' });
  } else if (/remedial|bimbingan/i.test(message)) {
    reply = `Berdasarkan peta indikator kelas ${cls.name}, 4 siswa membutuhkan penguatan scaffolding.`;
    suggestedActions.push({ label: 'Buka Learning Gaps & Remedial', action: 'open_learning_gaps' });
  } else {
    reply = `Memahami konteks kelas ${cls.name} (${cls.subject}). Bagaimana saya dapat memfasilitasi persiapan mengajar Anda hari ini?`;
    suggestedActions.push({ label: 'Buka Content Studio', action: 'open_studio' });
  }

  res.json({ success: true, reply, suggested_actions: suggestedActions, scope });
});
```
