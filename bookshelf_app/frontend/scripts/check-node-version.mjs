const requiredMajor = 20;
const current = process.versions.node;
const currentMajor = Number(current.split(".")[0]);

if (Number.isNaN(currentMajor) || currentMajor < requiredMajor) {
  console.error(`Node.js ${requiredMajor}以上が必要です。現在: v${current}`);
  console.error("nodebrewを使っている場合は `nodebrew use v22.13.1` を実行してください。");
  process.exit(1);
}
