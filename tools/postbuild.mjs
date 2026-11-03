// Batch A: lightweight postbuild. Full Hardware-learning checkers can be added later.
import { pagesBasePath } from "./is-ci.mjs";
import { existsSync } from "node:fs";

const basePath = pagesBasePath();
if (basePath !== "") {
  if (!existsSync("out")) {
    console.error("Expected static export directory `out/` when PAGES_BASE_PATH is set.");
    process.exit(1);
  }
  console.log(`Pages export OK (basePath=${basePath}).`);
} else {
  console.log(
    "Base-path export check skipped. Run with `PAGES_BASE_PATH=/Quant-trading-learn npm run build` or `CI=1 npm run build`.",
  );
}
process.exit(0);
