#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${BUILD_DIR:-$PROJECT_DIR/.build}"
mkdir -p "$BUILD_DIR/cheatsheet" "$BUILD_DIR/practice"
command -v xelatex >/dev/null || { echo '请安装含 ctex、Fandol、TikZ 的 TeX Live / MacTeX，并将 xelatex 加入 PATH。' >&2; exit 1; }
for doc in cheatsheet practice; do
  (cd "$PROJECT_DIR/$doc" && xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory="$BUILD_DIR/$doc" main.tex > "$BUILD_DIR/$doc/run1.txt")
  (cd "$PROJECT_DIR/$doc" && xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory="$BUILD_DIR/$doc" main.tex > "$BUILD_DIR/$doc/run2.txt")
  (cd "$PROJECT_DIR/$doc" && xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory="$BUILD_DIR/$doc" main.tex > "$BUILD_DIR/$doc/run3.txt")
done
cp "$BUILD_DIR/cheatsheet/main.pdf" "$PROJECT_DIR/CS5486-期中Cheatsheet-双面五栏.pdf"
cp "$BUILD_DIR/practice/main.pdf" "$PROJECT_DIR/CS5486-期中Cheatsheet-配套例题与解析.pdf"
echo '两份 PDF 已编译。日志位于 .build/；内容与版式验收另见验证说明。'
