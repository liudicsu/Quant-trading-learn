// Quiz grading check (R30). Quiz.tsx grades with a zero-based `answer` index into `options`.
// Checks: every Quiz parses, answer is in range, zh/en have the same IDs, same option count and same answer,
// plus semantic assertions for known-sensitive questions.
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
const R = new URL("..", import.meta.url).pathname;
let errors = 0;
const fail = (m) => { errors++; console.log("FAIL " + m); };
function quizzes(file) {
  const t = fs.readFileSync(file, "utf8"), out = new Map();
  for (const m of t.matchAll(/<Quiz\s+id="([^"]+)"[\s\S]*?options=\{(\[[\s\S]*?\])\}\s+answer=\{(\d+)\}/g)) {
    let opts;
    try { opts = vm.runInNewContext(m[2], {}, { timeout: 50 }); if (!Array.isArray(opts)) throw 0; } catch { fail(`${file}: ${m[1]} options not parseable`); continue; }
    const a = Number(m[3]);
    if (a < 0 || a >= opts.length) fail(`${file}: ${m[1]} answer ${a} out of range`);
    out.set(m[1], { opts, a });
  }
  return out;
}
const dirs = [];
for (const p of fs.readdirSync(R + "src/content")) for (const l of fs.readdirSync(path.join(R, "src/content", p))) dirs.push(path.join(R, "src/content", p, l));
let n = 0; const all = { zh: new Map(), en: new Map() };
for (const d of dirs) {
  const zh = quizzes(d + "/zh.mdx"), en = quizzes(d + "/en.mdx");
  for (const [id, q] of zh) { if (all.zh.has(id)) fail(`${d}: quiz id ${id} duplicated across lessons (R54: ids must be site-unique)`); all.zh.set(id, q); n++;
    const e = en.get(id);
    if (!e) { fail(`${d}: ${id} missing in en`); continue; }
    if (e.opts.length !== q.opts.length) fail(`${d}: ${id} option count zh ${q.opts.length} en ${e.opts.length}`);
    if (e.a !== q.a) fail(`${d}: ${id} answer zh ${q.a} en ${e.a}`);
  }
  for (const [id, q] of en) { all.en.set(id, q); if (!zh.has(id)) fail(`${d}: ${id} missing in zh`); }
}
// semantic assertions: [id, lang, substring that must be the graded-correct option, substring that must be graded wrong]
const SEM = [
  ["p6mrc-q5", "zh", "不是交易信号", "卖出信号"],
  ["p6mrc-q5", "en", "not a trade signal", "A sell signal"],
  ["cb-605", "zh", "排除特殊处理订单", "你自己账户的所有订单"],
  ["cb-605", "en", "excluding special-handling orders", "Every order in your own account"],
];
for (const [id, lang, right, wrong] of SEM) {
  const q = all[lang].get(id);
  if (!q) { fail(`${id}/${lang} not found`); continue; }
  const correct = q.opts[q.a];
  if (!correct.includes(right)) fail(`${id}/${lang}: graded-correct option is "${correct}"`);
  const wi = q.opts.findIndex((o) => o.includes(wrong));
  if (wi < 0 || wi === q.a) fail(`${id}/${lang}: "${wrong}" must exist and be graded wrong`);
  else console.log(`ok   ${id}/${lang}: answer=${q.a} "${correct}" correct; "${q.opts[wi]}" graded wrong`);
}
// stem/explanation assertions (R45): cb-605 asks about report COVERAGE, and must say plain NMLOs get no ES.
const STEM = [
  ["src/content/p2/costs-in-backtest/zh.mdx", "cb-605", ["覆盖订单范围", "普通 NMLO 不计 ES"], ["有效价差统计包含"]],
  ["src/content/p2/costs-in-backtest/en.mdx", "cb-605", ["covered-order scope", "plain NMLOs get no ES"], ["effective-spread statistics include"]],
];
for (const [file, id, must, mustNot] of STEM) {
  const line = fs.readFileSync(path.join(R, file), "utf8").split("\n").find((l) => l.includes(`id="${id}"`)) || "";
  if (!line) { fail(`${file}: ${id} not found`); continue; }
  const miss = must.filter((s) => !line.includes(s)), bad = mustNot.filter((s) => line.includes(s));
  if (miss.length || bad.length) fail(`${file}: ${id} stem/explanation missing ${JSON.stringify(miss)} or contains ${JSON.stringify(bad)}`);
  else console.log(`ok   ${id} stem/explanation: ${file.split("/").pop()}`);
}
// R64: quiz fields must not refer to an option by display or source position (shuffle would make it wrong).
// Catch "option 1", "first/last option", "第N项", "第一个选项", "最后一项", "第二选", and similar.
// Do not flag rule names such as "option 606", or ordinary words such as "哪一项" / "equity options".
const POS_RE = /\boption\s*(?:#|no\.?\s*|number\s*)?(?:[1-9]|one|two|three|four|five|1st|2nd|3rd|4th|5th)\b|\b(?:the\s+)?(?:first|second|third|fourth|fifth|last)\s+option\b|第\s*[一二三四五六七八九十两零\d]+\s*(?:项|个选项|个选择|选)|最后一项|最后一个选项|选项\s*[一二三四五六七八九十两零\d]+/i;
for (const d of dirs) {
  for (const lang of ["zh", "en"]) {
    const file = `${d}/${lang}.mdx`;
    const text = fs.readFileSync(file, "utf8");
    for (const m of text.matchAll(/<Quiz\s+id="([^"]+)"([\s\S]*?)\/>/g)) {
      const id = m[1], body = m[2];
      const fields = [];
      const q = body.match(/question="([^"]*)"/); if (q) fields.push(["question", q[1]]);
      const e = body.match(/explanation="([^"]*)"/); if (e) fields.push(["explanation", e[1]]);
      const o = body.match(/options=\{(\[[\s\S]*?\])\}/); if (o) fields.push(["options", o[1]]);
      for (const [field, val] of fields) {
        if (POS_RE.test(val)) fail(`${file}: ${id} ${field} refers to an option by position`);
      }
    }
  }
}
// R49: answer-position distribution after the deterministic shuffle used by Quiz.tsx (keep in sync).
function fnv1a(s) { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; } return h >>> 0; }
function optionOrder(id, n) {
  let s = fnv1a(id);
  const a = Array.from({ length: n }, (_, i) => i);
  for (let i = n - 1; i > 0; i--) { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; const j = Math.floor((s / 4294967296) * (i + 1)); const tmp = a[i]; a[i] = a[j]; a[j] = tmp; }
  return a;
}
const pos = {};
for (const [id, q] of all.zh) { const p = optionOrder(id, q.opts.length).indexOf(q.a); pos[p] = (pos[p] || 0) + 1; }
const total = all.zh.size;
for (const [p, c] of Object.entries(pos)) if (c / total > 0.5) fail(`displayed answer position ${+p + 1} holds ${c}/${total} (> 50%)`);
console.log(`ok   displayed answer positions: ${Object.entries(pos).sort().map(([p, c]) => `#${+p + 1}=${c}`).join(" ")} of ${total}`);
console.log(errors ? `quiz check FAILED (${errors})` : `quiz check PASSED: ${n} quiz pairs zh/en, ${SEM.length} semantic assertions`);
process.exit(errors ? 1 : 0);
