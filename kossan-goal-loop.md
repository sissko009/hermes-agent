# Hermes /goal ループ — こっさん運用ガイド

> このファイルは `.hermes-parallel/hermes-agent/` の kossan-custom ブランチに置く。
> 親リポジトリの設計書: `kossan-hq/guidelines/goal-loop.md`

---

## Hermes の役割（orchestrator）

Hermes はコードを書かない。**委譲と統合だけ**を担う。

```text
こっさんの依頼
  ↓
Hermes が /goal を展開（Codex 用 + Claude Code 用）
  ↓
Codex が実装 → Claude Code がレビュー
  ↓
PASS なら完了報告 / BLOCKED なら修正 /goal を Codex に再発行
```

---

## Hermes が /goal を受け取った時の動作

### 1. /goal を解析する

受け取った /goal から以下を抽出する:

- **what**: 何を作るか（対象と仕様参照）
- **done**: 完了条件（検証コマンドで判定できるか確認）
- **verifier**: 検証コマンド（なければ補完する）

Done 条件が曖昧な場合（「良くして」「直して」等）は、こっさんに確認する前に Hermes が具体化する。

### 2. Codex への /goal を作成する

```text
/goal <what> per <仕様参照>.
Done means <具体的な完了条件>.
Verifier: <検証コマンド>
```

仕様参照は必ず kossan-hq 内のファイルパスで指定する。

### 3. Claude Code へのレビュー /goal を作成する

```text
/goal Review the Codex diff for <対象>.
Done means PASS or BLOCKED with findings prioritized by severity.
Findings: CRITICAL/MAJOR/MINOR | file:line | issue | fix suggestion
Review checklist:
1. バグ・破綻（動かないコード・例外未処理）
2. セキュリティ（credentials 漏れ・injection）
3. 仕様漏れ（Done 条件との差分）
4. ハーネスルール準拠（guidelines/harness-engineering.md §0.5）
5. リグレッション（既存テスト・既存機能への影響）
```

### 4. 結果を集約してこっさんに報告する

```text
## /goal 完了報告

### 実装: Codex
- 変更ファイル: <リスト>
- verifier 結果: PASS / FAIL

### レビュー: Claude Code
- 判定: PASS / BLOCKED
- findings: <件数と重大度>

### 総合判定: PASS / BLOCKED / ESCALATE
```

---

## BLOCKED 時の対応

### 修正 /goal の発行（最大3回）

```text
/goal Fix the following findings per Claude Code review.
Done means all CRITICAL and MAJOR findings are resolved and verifier passes.
Findings to fix:
- [CRITICAL] <file:line>: <issue>
- [MAJOR] <file:line>: <issue>
Verifier: <前回と同じコマンド>
```

### 3回の修正ループで PASS しない場合（harness-engineering.md と統一）

こっさんにエスカレートする。修正ループを自分で続けない。

```text
## エスカレーション

/goal「<内容>」が3回の修正ループで PASS しませんでした。

残存 findings:
- [CRITICAL] <詳細>

こっさんの判断が必要です。
選択肢:
A. 仕様を変更する
B. 手動で修正する
C. このタスクをいったん保留する
```

---

## Hermes が書いてはいけないこと

- 自分でコードを書く（実装は Codex に委譲）
- Claude Code の BLOCKED 判定を覆す（Hermes は最終評価しない）
- verifier を走らせずに PASS と判断する
- こっさんに確認なしで仕様を変更する
- `.env` / `credentials/` を含む差分を Codex に渡す

---

## kossan-hq との連携

このファイルは kossan-hq の管理外（gitlink なし）。
設計書本体は `kossan-hq/guidelines/goal-loop.md` が正本。

変更が必要な時:
1. こちら（hermes 側）を更新 → `git commit` → `git push origin kossan-custom`
2. 必要に応じて `kossan-hq/guidelines/goal-loop.md` も更新

---

更新履歴:
- 2026-05-23: 初版作成（goal-loop.md の Hermes 側実装ガイド）
