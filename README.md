# dotfiles-claude

Claude Code の userSettings(`~/.claude/`)。公開可能な `base` と手元のみの `private` を分離し、`install.sh` でマージして配置する。

## 構成

```
claude/
  settings.base.json     # 公開可
  settings.private.json  # gitignore・手元のみ・任意
  hooks/notify.py        # macOS 通知フック
install.sh               # base+private を merge → ~/.claude/settings.json 生成、notify.py を symlink
```

## インストール

```bash
git clone <this-repo> dotfiles-claude && cd dotfiles-claude
./install.sh   # 環境依存設定が要るなら claude/settings.private.json を先に作成(任意)
```

必要: `python3` と macOS の `osascript`(通知用。他OSでは通知のみ無効で他は動作)。

`~/.claude/settings.json` は生成物。変更は `settings.base.json` / `settings.private.json` を編集して `./install.sh` を再実行する(`notify.py` は symlink なので即反映)。

## ポイント

- **権限**: `defaultMode: "auto"`(安全チェック付きの自動承認)。`deny` で `.env` / `secrets` / `~/.ssh` / `~/.aws` の読み取りと `rm -rf /` を恒久ブロック。
- **通知**: `Notification` / `Stop` で `notify.py` が macOS 通知(プロジェクト名・セッションID・内容を表示、柔らかい音)。音は `notify.py` 冒頭の定数で変更可。
