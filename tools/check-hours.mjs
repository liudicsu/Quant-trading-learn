// Cross-file hour consistency check (R31; decimal hours such as 0.25/0.5 accepted since 2026-11-08). Sources: src/lib/curriculum.ts (truth), README.md,
// messages/zh.json, messages/en.json, docs/CURRICULUM_V2.md (knowledge map, phase table, section 5), MDX line 3.
import fs from "node:fs";
const R = new URL("..", import.meta.url).pathname;
const rd = (p) => fs.readFileSync(R + p, "utf8");
let errors = 0;
const fail = (m) => { errors++; console.log("FAIL " + m); };
let lastErr = 0;
const ok = (m) => { if (errors === lastErr) console.log("ok   " + m); lastErr = errors; };

// depth-0 sum of "<num>h" inside a string (ignores numbers inside nested parentheses)
function sumTop(s) {
  let d = 0, out = "";
  for (const ch of s) {
    if (ch === "(" || ch === "（") d++;
    else if (ch === ")" || ch === "）") d = Math.max(0, d - 1);
    else if (d === 0) out += ch;
  }
  return [...out.matchAll(/(\d+(?:\.\d+)?)\s*h\b/g)].reduce((a, m) => a + Number(m[1]), 0);
}
// text inside the outer parenthesis that opens just before "**N 学时/hours**"
function headerParts(line) {
  const m = line.match(/\*\*(\d+(?:\.\d+)?) (?:学时|hours)\*\*/);
  if (!m) return null;
  const open = Math.max(line.lastIndexOf("(", m.index), line.lastIndexOf("（", m.index));
  let d = 0, end = -1;
  for (let i = open; i < line.length; i++) {
    const c = line[i];
    if (c === "(" || c === "（") d++;
    if (c === ")" || c === "）") { d--; if (d === 0) { end = i; break; } }
  }
  const inner = line.slice(m.index + m[0].length, end);
  return { total: Number(m[1]), sub: sumTop(inner) };
}

const cur = rd("src/lib/curriculum.ts");
const phaseBlocks = [...cur.matchAll(/const phase_(P\d)_lessons[\s\S]*?(?=const phase_P\d_lessons|export |$)/g)];
const lessons = [];
for (const pb of phaseBlocks) {
  for (const m of pb[0].matchAll(/slug: "([^"]+)",[\s\S]*?\n    hours: (\d+(?:\.\d+)?),[\s\S]*?hourBasis: "([^"]*)"/g)) {
    lessons.push({ phase: pb[1], slug: m[1], hours: Number(m[2]), basis: m[3] });
  }
}
const full = lessons.reduce((a, l) => a + l.hours, 0);
const p0 = lessons.filter((l) => l.phase === "P0").reduce((a, l) => a + l.hours, 0);
const metaFull = Number(cur.match(/hoursFull: (\d+(?:\.\d+)?)/)[1]);
const metaSkip = Number(cur.match(/hoursSkipFoundations: (\d+(?:\.\d+)?)/)[1]);
const metaCount = Number(cur.match(/lessonCount: (\d+)/)[1]);
console.log(`curriculum.ts: lessons=${lessons.length} full=${full} P0=${p0} skipP0=${full - p0}`);
(lessons.length === metaCount ? ok : fail)(`lessonCount ${metaCount} vs parsed ${lessons.length}`);
(full === metaFull ? ok : fail)(`hoursFull ${metaFull} vs sum ${full}`);
(full - p0 === metaSkip ? ok : fail)(`hoursSkipFoundations ${metaSkip} vs ${full - p0}`);
for (const l of lessons) { const s = sumTop(l.basis); if (s !== l.hours) fail(`hourBasis ${l.slug}: ${s} != ${l.hours}`); }
ok("hourBasis sub-items checked for all lessons");
const range = cur.match(/hoursRangeLabel: \{\s*zh: "([^"]+)",\s*en: "([^"]+)"/);
for (const s of [range[1], range[2]]) (s.includes(`${full}h`) && s.includes(`${full - p0}h`) ? ok : fail)(`hoursRangeLabel: ${s.slice(0, 40)}…`);

const totalsIn = (name, s) => (s.includes(String(full)) && s.includes(String(full - p0)) ? ok : fail)(`${name} mentions ${full}/${full - p0}`);
totalsIn("README.md", rd("README.md").match(/\*\*Hours:\*\*.*/)[0]);
totalsIn("messages/zh.json", JSON.parse(rd("messages/zh.json")).home?.placeholderNote ?? rd("messages/zh.json").match(/"placeholderNote": "([^"]+)"/)[1]);
totalsIn("messages/en.json", JSON.parse(rd("messages/en.json")).home?.placeholderNote ?? rd("messages/en.json").match(/"placeholderNote": "([^"]+)"/)[1]);

// MDX headers
let mdxN = 0;
for (const l of lessons) for (const lang of ["zh", "en"]) {
  const p = `src/content/${l.phase.toLowerCase()}/${l.slug}/${lang}.mdx`;
  const line = rd(p).split("\n").find((x) => /\*\*\d+(?:\.\d+)? (学时|hours)\*\*/.test(x));
  const h = line && headerParts(line);
  if (!h) { fail(`${p}: no hours header`); continue; }
  if (h.total !== l.hours) fail(`${p}: header ${h.total} != ${l.hours}`);
  if (h.sub !== l.hours) fail(`${p}: header sub-items ${h.sub} != ${l.hours}`);
  mdxN++;
}
ok(`MDX headers checked: ${mdxN}`);

// V2
const v2 = rd("docs/CURRICULUM_V2.md");
for (const l of lessons) {
  const m = v2.match(new RegExp("\\| `" + l.slug + "` \\| (P\\d) \\| (\\d+(?:\\.\\d+)?) \\|"));
  if (!m || Number(m[2]) !== l.hours || m[1] !== l.phase) fail(`V2 knowledge map ${l.slug}: ${m ? m[2] : "missing"} != ${l.hours}`);
}
ok("V2 knowledge-map rows checked");
const phases = [...new Set(lessons.map((l) => l.phase))];
for (const ph of phases) {
  const ls = lessons.filter((l) => l.phase === ph), h = ls.reduce((a, l) => a + l.hours, 0);
  const t = v2.match(new RegExp("\\n\\| " + ph + " \\|[^|]*\\| (\\d+) \\| (\\d+(?:\\.\\d+)?)h \\|"));
  if (!t || Number(t[1]) !== ls.length || Number(t[2]) !== h) fail(`V2 phase table ${ph}: ${t ? t[2] : "missing"} != ${h}`);
  const s = v2.match(new RegExp("### " + ph + " · .*— (\\d+(?:\\.\\d+)?)h / (\\d+) 课"));
  if (!s || Number(s[1]) !== h || Number(s[2]) !== ls.length) fail(`V2 section 5 heading ${ph}: ${s ? s[1] : "missing"} != ${h}`);
}
ok("V2 phase table + section 5 phase headings checked");
const sec5 = v2.slice(v2.indexOf("## 5."), v2.indexOf("\n## 6.") > 0 ? v2.indexOf("\n## 6.") : undefined);
for (const l of lessons) {
  const m = sec5.match(new RegExp("`" + l.slug + "`[\\s\\S]*?\\*\\*Hours:\\*\\* (\\d+(?:\\.\\d+)?)h"));
  if (!m || Number(m[1]) !== l.hours) fail(`V2 section 5 ${l.slug}: ${m ? m[1] : "missing"} != ${l.hours}`);
}
ok("V2 section 5 per-lesson Hours lines checked");
const tot = v2.match(/精确合计：\*\*(\d+(?:\.\d+)?)h 全量 \/ (\d+(?:\.\d+)?)h 跳过 P0\*\*/);
(tot && Number(tot[1]) === full && Number(tot[2]) === full - p0 ? ok : fail)(`V2 total line ${tot ? tot[1] + "/" + tot[2] : "missing"}`);
console.log(errors ? `hours check FAILED (${errors})` : `hours check PASSED: ${lessons.length} lessons, ${full}h full / ${full - p0}h skip-P0, P0=${p0}h`);
process.exit(errors ? 1 : 0);
