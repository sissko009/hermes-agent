# こっさん運用ポリシー（HERMES 側作業時の遵守事項）

このドキュメントは、HERMES（`.hermes-parallel/hermes-agent/`）を触る全セッションが従うべき共通ルール。  
上位ポリシーは親リポジトリ [kossan-hq](https://github.com/sissko009/kossan-hq) の `.claude/rules/branches.md` と整合させる。

## 1. リポジトリと remote 構成

| remote | URL | 役割 |
|---|---|---|
| `origin` | `https://github.com/sissko009/hermes-agent.git` | **push先**（こっさんのfork） |
| `upstream` | `https://github.com/NousResearch/hermes-agent.git` | **pull元**（公式OSS追随） |

**絶対ルール**:
- `upstream` への push は**物理的にも論理的にも不可**（他人のリポジトリ）
- `origin`（fork）への force push は**こっさん明示承認がある時のみ**

## 2. ブランチ運用

| ブランチ | 役割 | 誰が触るか |
|---|---|---|
| `main` | NousResearch公式追随用。自動merge only | 公式sync専用。手で書かない |
| `kossan-custom` | こっさん個人のカスタマイズ | 普段の作業ブランチ |
| `kossan-custom/<topic>` | 大きな変更のフィーチャーブランチ | topic別に分けたい時 |

**絶対ルール**:
- 手動の編集commitは**必ず `kossan-custom` 系ブランチ**で行う
- `main` に直接commit/pushしない（`main` は upstream の鏡）
- `main` 更新は `git fetch upstream && git merge --ff-only upstream/main` のみ許可

## 3. commit 作法

- **1 commit = 1 論理変更**。27ファイル一括WIPは初回退避だけ。以後は論理単位で小さく
- コミットメッセージの接頭辞は kossan-hq 側と揃える:
  - `feat(scope): ...` - 新機能
  - `fix(scope): ...` - バグ修正
  - `docs(scope): ...` - ドキュメント
  - `refactor(scope): ...` - 挙動変えないリファクタ
  - `WIP: ...` - 途中経過（リモート退避目的のみ）
- scope は gateway / docs / tests / memory など、編集範囲が分かる単語
- 破壊的変更や秘密情報の混入が疑われる時は commit 前にこっさんに確認

## 4. push 作法

```bash
# 通常の push
git push origin kossan-custom

# rebase 後など force が必要な時
git push origin kossan-custom --force-with-lease  # --force ではなく lease を使う
```

**禁止事項**:
- `git push --force` そのままは禁止。`--force-with-lease` を使う
- `git push origin main` は禁止（mainはupstreamの鏡なので）
- `--no-verify` でフック飛ばし禁止
- `--no-gpg-sign` でsign飛ばし禁止

## 5. 公式更新の取り込み手順

NousResearch が新機能をリリースした時は以下の順で取り込む:

```bash
# 1. upstream を fetch
git fetch upstream

# 2. main を公式最新に FF（ローカル / fork 両方）
git checkout main
git merge --ff-only upstream/main
git push origin main

# 3. kossan-custom を main に rebase（コンフリクト解消は手動）
git checkout kossan-custom
git rebase main

# 4. fork へ push（rebase後なので force-with-lease）
git push origin kossan-custom --force-with-lease
```

**禁止事項**:
- `main` に `kossan-custom` を merge しない（汚染防止）
- 公式 PR 未採用のコードを `main` に混ぜない

## 6. 秘密情報の取り扱い

- `.env`, `credentials/`, API キー, トークン, webhook URL を**絶対に commit しない**
- wrangler secret, LINE channel secret, Discord webhook 等は環境変数で渡す
- `git diff` で `password` `token` `api_key` `secret` 等の語を含む変更がないか commit 前に確認
- 過去に混入していた場合は `git filter-repo` 等で履歴から完全除去して force-with-lease

## 7. 複数セッション協調

HERMES 作業場所に同時に触れる可能性のあるクライアント:
- VSCode Claude Code（こっさん PC ローカル）
- Claude Code 別 PC セッション
- 将来的な自動トリガー（cron, RemoteTrigger 等）

**ルール**:
- 作業開始時に `git fetch origin && git status` で最新状態確認
- push 前に `git pull --rebase origin kossan-custom` で衝突を吸収
- push が rejected されたら rebase → push をリトライ（最大3回）、それ以上は人間判断
- 自動トリガーを追加する場合は push 先を別ブランチ（例: `auto/kossan-custom`）に隔離し、親kossan-hq と同じパターンを踏襲

## 8. 作業ログ

- 大きな変更セッションは `memory/YYYY-MM-DD.md` に要点を残す
- 「なぜ変えたか」「どこを見直せば戻せるか」を1行ずつ書く
- 実装メモは `DESIGN_PRINCIPLES.md` `DISCORD_GATEWAY_ENV_MAP.md` 等の専用docに追記

## 9. 親 kossan-hq との連動

HERMES は kossan-hq の**管理外**の並行作業場所（gitlink ではない）。つまり:
- HERMES の変更は kossan-hq に自動で波及しない
- 逆に kossan-hq 側の変更も HERMES に波及しない
- 両方を同期させたい場合は**明示的に**両方で commit/push する

もし将来 HERMES を kossan-hq の submodule として正式登録する場合は、親側に `.gitmodules` を作成し、`git submodule add` で登録し直す。

## 10. この workspace の正本パス

- 実運用で書き込み対象にする Hermes 本体は **`/mnt/c/Users/user/OneDrive/デスクトップ/kossan-hq/.hermes-parallel/hermes-agent` の1つだけ**。
- gateway / Discord / cron / ローカルCLI で Hermes 本体を触る時は、まずこのパスを見てから作業する。
- 別の writable clone を増やさない。役割分離は clone ではなく **profile** で行う。
- 並行ブランチや検証が必要なら clone を増やさず **`git worktree`** を使う。
- 実行状態の切替や profile 移行をする時は、どの service / script / alias がどのパスを見ているかを先に確認する。

## 11. 迷ったら

- こっさんに聞く
- `--force` を打つ前に聞く
- upstream に push しようとした時点で止まる
- main を書き換えようとした時点で止まる
- 指示が曖昧なら曖昧なまま実行しない

---

**更新履歴**
- 2026-04-19: 初版作成（sissko009 fork 切替・kossan-custom ブランチ導入に合わせて策定）
