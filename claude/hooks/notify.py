#!/usr/bin/env python3
"""Claude Code 通知フック。

stdin でフックの JSON を受け取り、macOS 通知を出す。
引数 $1:
  notify -> 確認待ち(Notification イベント)。Claude の依頼内容を本文に出す。
  done   -> 作業完了(Stop イベント)。直近の Claude 発言の冒頭を本文に出す。

タイトル=状態、サブタイトル=プロジェクト名 + セッションID(先頭8桁)、本文=内容。
何があっても通知の失敗でフックを壊さないよう全体を握りつぶす。
"""
import sys
import os
import json
import subprocess

# 優しめのシステムサウンド。/System/Library/Sounds/ にある名前。
# 候補(柔らかい順の目安): Purr, Tink, Pop, Morse, Submarine, Glass, Hero, Ping, Sosumi, Funk, Bottle, Frog
SOUND_NOTIFY = "Tink"   # 確認待ち: 軽くて気づける
SOUND_DONE = "Purr"     # 完了: 柔らかい


def read_input():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def last_assistant_text(path, maxbytes=262144, limit=80):
    """transcript(JSONL)の末尾から直近の assistant テキストを拾う。best-effort。"""
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - maxbytes))
            lines = f.read().decode("utf-8", "replace").splitlines()
        for line in reversed(lines):
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("type") != "assistant":
                continue
            content = (o.get("message") or {}).get("content")
            if isinstance(content, list):
                for block in reversed(content):
                    if isinstance(block, dict) and block.get("type") == "text":
                        t = " ".join(block.get("text", "").split())
                        if t:
                            return t[:limit]
            elif isinstance(content, str):
                t = " ".join(content.split())
                if t:
                    return t[:limit]
    except Exception:
        pass
    return ""


def osa_str(s):
    """AppleScript 文字列リテラルにエスケープ。"""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "done"
    d = read_input()

    proj = os.path.basename((d.get("cwd") or "").rstrip("/")) or "claude"
    sid = (d.get("session_id") or "")[:8]
    subtitle = proj + (" · " + sid if sid else "")

    if kind == "notify":
        title = "⏳ Please Check"
        body = " ".join((d.get("message") or "確認が必要です").split())
        sound = SOUND_NOTIFY
    else:
        title = "✅ Done"
        snippet = last_assistant_text(d.get("transcript_path") or "")
        body = snippet or "作業が完了しました"
        sound = SOUND_DONE

    script = "display notification {} with title {} subtitle {} sound name {}".format(
        osa_str(body), osa_str(title), osa_str(subtitle), osa_str(sound)
    )
    try:
        subprocess.run(
            ["osascript", "-e", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


if __name__ == "__main__":
    main()
