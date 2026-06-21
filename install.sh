#!/usr/bin/env bash
#
# Claude Code userSettings インストーラ
#
# claude/settings.base.json (公開可) と claude/settings.private.json (gitignore・手元のみ)
# を top-level マージして ~/.claude/settings.json を生成する。
# hooks/notify.py は symlink する(秘密情報を含まないため repo に追従させる)。
#
# private が無くても動く(base だけで生成)。
#
# 使い方:
#   ./install.sh
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_DIR/claude"
DST="$HOME/.claude"
BASE="$SRC/settings.base.json"
PRIV="$SRC/settings.private.json"
OUT="$DST/settings.json"
ts="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$DST/hooks"

# --- settings.json を base + private のマージで生成 -------------------------
if [ ! -f "$BASE" ]; then
  echo "ERROR: $BASE が見つかりません" >&2
  exit 1
fi

if [ -e "$OUT" ] || [ -L "$OUT" ]; then
  mv "$OUT" "$OUT.bak.$ts"
  echo "backed up existing settings.json -> settings.json.bak.$ts"
fi

python3 - "$BASE" "$PRIV" "$OUT" <<'PY'
import json, os, sys
base_path, priv_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
with open(base_path, encoding="utf-8") as f:
    data = json.load(f)
if os.path.exists(priv_path):
    with open(priv_path, encoding="utf-8") as f:
        priv = json.load(f)
    priv.pop("_comment", None)
    data.update(priv)  # top-level override（base と private はキーが重ならない設計）
    merged = "base + private"
else:
    merged = "base のみ（private 無し）"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"generated settings.json ({merged})")
PY

# --- hooks/notify.py を symlink --------------------------------------------
src_hook="$SRC/hooks/notify.py"
dst_hook="$DST/hooks/notify.py"
if [ -L "$dst_hook" ] && [ "$(readlink "$dst_hook")" = "$src_hook" ]; then
  echo "ok (already linked): hooks/notify.py"
else
  if [ -e "$dst_hook" ] || [ -L "$dst_hook" ]; then
    mv "$dst_hook" "$dst_hook.bak.$ts"
    echo "backed up existing hooks/notify.py -> notify.py.bak.$ts"
  fi
  ln -s "$src_hook" "$dst_hook"
  echo "linked: hooks/notify.py -> $src_hook"
fi
chmod +x "$src_hook" 2>/dev/null || true

echo
echo "Done. 次のセッションから有効です。"
echo
echo "注意:"
echo "  - settings.json は『生成物』。設定変更は settings.base.json / settings.private.json を編集して再実行する。"
echo "  - 環境依存設定が必要なら claude/settings.private.json を作成してから実行(任意)。"
