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
  for (const [id, q] of zh) { all.zh.set(id, q); n++;
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
console.log(errors ? `quiz check FAILED (${errors})` : `quiz check PASSED: ${n} quiz pairs zh/en, ${SEM.length} semantic assertions`);
process.exit(errors ? 1 : 0);
