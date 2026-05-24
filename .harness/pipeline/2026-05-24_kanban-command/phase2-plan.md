## Sprint Contract: /kanban command first slice

### ゴール
`/kanban <request>` を Hermes の built-in slash command として追加し、CLI と gateway の両方で既存の `todo` + `delegate_task` 前提の kanban 実行プロンプトへ導線化する。

### 合格基準

#### 機能（開発リーダー判定）
- [ ] `COMMAND_REGISTRY` に `/kanban <request>` が追加され、help/known commands に露出する
- [ ] CLI で `/kanban Build OAuth login` を実行すると、agent 向け kanban 実行プロンプトが queue される
- [ ] CLI で `/kanban` を実行すると usage を返し、queue しない
- [ ] gateway で `/kanban Build OAuth login` を受けると、agent に渡す `message` が kanban 実行プロンプトへ変換される
- [ ] gateway で `/kanban` を受けると usage を返す

#### 品質（開発リーダー判定）
- [ ] kanban 用の文面生成は shared helper に集約され、CLI/gateway で重複しない
- [ ] 既存 `/goal` や `/plan` の挙動を壊さない

#### AI行動契約（Evaluator判定）
- [ ] 前提・不確実性・矛盾を明示した
- [ ] 変更範囲がSprint Contract内に収まっている
- [ ] 書く前に対象ファイル・呼び出し元・共有utilityを確認した
- [ ] テスト/検証が「意図」を確認している
- [ ] skipped / 未検証 / 残リスクを隠していない

### スコープ外（今回やらないこと）
- [ ] 永続Kanban DBや新しい board UI の実装
- [ ] `kanban` 専用 tool の新設
- [ ] 複数ボード管理や board history 表示
