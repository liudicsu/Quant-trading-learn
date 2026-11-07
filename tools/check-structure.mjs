// zh/en structure check (R37): same heading-level sequence and same Quiz ID order per lesson.
// Distinguishes "missing" (sets differ) from "order-only" (same sets, different order).
import fs from "node:fs";
import path from "node:path";
const R = new URL("..", import.meta.url).pathname;
let errors = 0, n = 0;
function shape(f) {
  let inCode = false; const heads = [], quiz = [];
  for (const l of fs.readFileSync(f, "utf8").split("\n")) {
    if (l.startsWith("```")) { inCode = !inCode; continue; }
    if (inCode) continue;
    const h = l.match(/^(#{2,4}) /); if (h) heads.push(h[1].length);
    const q = l.match(/<Quiz id="([^"]+)"/); if (q) quiz.push(q[1]);
  }
  return { heads, quiz };
}
for (const p of fs.readdirSync(R + "src/content").sort()) for (const l of fs.readdirSync(path.join(R, "src/content", p)).sort()) {
  const d = path.join(R, "src/content", p, l), zh = shape(d + "/zh.mdx"), en = shape(d + "/en.mdx"); n++;
  const qs = (a) => [...a].sort().join(",");
  if (qs(zh.quiz) !== qs(en.quiz)) { errors++; console.log(`FAIL ${p}/${l}: quiz ID sets differ (missing)`); }
  else if (zh.quiz.join() !== en.quiz.join()) { errors++; console.log(`FAIL ${p}/${l}: quiz order-only difference`); }
  if (zh.heads.length !== en.heads.length) { errors++; console.log(`FAIL ${p}/${l}: heading count zh ${zh.heads.length} en ${en.heads.length} (missing)`); }
  else if (zh.heads.join() !== en.heads.join()) { errors++; console.log(`FAIL ${p}/${l}: heading level/order-only difference`); }
}
console.log(errors ? `structure check FAILED (${errors})` : `structure check PASSED: ${n} lessons, zh/en heading levels and quiz order match`);
process.exit(errors ? 1 : 0);
