---
name: renpy-tl-manager
description: 管理 Ren'Py 正體中文翻譯專案的進度、draft 切割、worker 分派、驗證與合併。當需要安排多個 .rpy 檔案、將單一檔案分批交給 worker，或驗收並回寫翻譯時使用；不要用於直接翻譯文本。
---

# Ren'Py 翻譯 manager

## 核心模型

- `progress.md` 只記錄每個翻譯檔是否完成：`[ ]` 或 `[x]`。
- 一個尚未完成檔案的暫時工作狀態由 `.renpy-tl/drafts/` 中的 manifest 表示，不要把 `worker_working`、`validation` 等操作狀態寫進 `progress.md`。
- 同一個原始翻譯檔同時只能有一份 active draft 與一個 worker。draft 合併並清理前，不得為同一檔案建立下一份 draft。
- manager 不直接翻譯文本；翻譯交給 `$renpy-tl-worker`。

第一版假設翻譯是由檔案前方依序往後處理，且每次切割的是連續的完整翻譯單位。不要把任意實體行數當成切割邊界。

## 檔案層級生命週期

對每個尚未完成檔案重複以下批次流程：

`選檔 -> 找既有 draft 或切割 -> worker 翻譯 -> worker-only 驗證 -> manager 完整驗證 -> 合併 -> 驗證原檔 -> 清理 draft`

完成原檔驗證後，若仍有未翻譯單位，先移除或封存該批次的 `.rpy` 與 `.json`，再建立下一批。整個檔案通過完整驗證、輸出 `NEXT_ACTION=mark_complete` 後，才能把 `progress.md` 的項目改成 `[x]`。

## 調度規則

1. 依 `progress.md` 的順序處理 `- [ ]` 項目；不要跳過目前驗收失敗的檔案去處理同一批次的下一個檔案。
2. 使用者沒有指定時，保留既有預設：本輪最多處理 2 個檔案，同時最多啟用 2 個 worker。worker 模型遵循使用者指定；未指定時使用目前預設的 `gpt-5.6-luna (Reasoning Medium)`。
3. 不同檔案可以平行處理，但同一原始檔只能有一個 active manifest 與一個 worker。
4. 建立 draft 前，掃描 `.renpy-tl/drafts/` 中的 JSON manifest：同一 `translation_file` 有一份就繼續它，有多份就停止並回報衝突，不要再切割。
5. 驗收結果為 `worker_continue` 時，繼續同一 draft；不要用下一個檔案取代它。相同 worker 在同一檔案最多繼續 2 次，仍未完成時要求交接並關閉，然後讓新的 worker 重新閱讀 guide 後接手同一 draft。
6. worker 不得修改 `progress.md` 或 `translation-guide.md`。manager 負責 review worker 回報中值得長期保存的 guide 建議。

## 建立或繼續 draft

若沒有 active manifest，使用：

```bash
python3 <skill-dir>/scripts/split_translation.py <translation-file> \
  --project-root <project-root> \
  --context-units <n> \
  --work-units <m>
```

`n` 與 `m` 是完整翻譯單位數，不是實體行數。draft 會放在專案內的 `.renpy-tl/drafts/`，並鏡像原始檔案的相對路徑，例如：

```text
game/tl/tChinese/day1.rpy
.renpy-tl/drafts/game/tl/tChinese/day1.lines-00100-00200.rpy
.renpy-tl/drafts/game/tl/tChinese/day1.lines-00100-00200.json
```

draft 包含一段已翻譯上下文，以及由一對下列註解包住的待翻譯範圍：

```text
# renpy-tl-draft: work-begin
...
# renpy-tl-draft: work-end
```

不要在每個翻譯單位中加入額外標記；`translate ... strings:` 也使用相同的一對工作標記。manifest 第一版只記錄：

```json
{
  "translation_file": "game/tl/tChinese/day1.rpy",
  "translation_file_lines": {"start": 100, "end": 200},
  "work_lines": {"start": 150, "end": 200},
  "draft_file": ".renpy-tl/drafts/game/tl/tChinese/day1.lines-00100-00200.rpy"
}
```

不需要 `version`、`part`、`context_units` 或 `assigned_units`。目前不使用 Git hash 或外部修改鎖定；流程假設 active draft 期間原始檔不被改動。
如果翻譯來源整體更新到新的版本，不嘗試遷移舊 draft；先清除 `.renpy-tl/drafts/` 下的 draft 與 manifest，再重新切割。

## worker 分派與 worker-only 驗證

分派時只把以下資料交給 worker：

- 指定的 draft `.rpy` 路徑；
- 專案根目錄的 `translation-guide.md`（若存在）；
- 明確要求使用 `$renpy-tl-worker`，且不得閱讀原始翻譯檔、其他 `.rpy`、`progress.md` 或 manifest。

worker 完成後可使用只讀 draft 的驗證：

```bash
python3 <skill-dir>/scripts/validation.py <draft-file> --worker
```

這個模式不讀取原始檔或 manifest：

- `NEXT_ACTION=worker_continue`：仍有未翻譯單位或 placeholder/tag 不一致，worker 繼續同一 draft；
- `NEXT_ACTION=worker_done`：draft 內的工作內容已完成，交回 manager；
- `NEXT_ACTION=manager_fix_structure`：工作標記或翻譯單位結構有問題，worker 不要自行修復標記，交回 manager。

## manager 完整驗證、合併與回寫

worker 回報 `worker_done` 後，manager 必須執行需要原始檔與 manifest 的完整 draft 驗證：

```bash
python3 <skill-dir>/scripts/validation.py <draft-file> \
  --manifest <manifest-file> \
  --project-root <project-root>
```

驗證會確認：

- draft 是否仍有未翻譯單位；
- translation unit、`translate` 標頭、來源位置註解、`old/new` 配對與縮排是否保留；
- worker 是否只改動工作範圍；
- Ren'Py tag、placeholder 與字串結構是否一致；
- manifest 行號範圍、工作標記與實際 draft 是否相符。

只有輸出 `NEXT_ACTION=merge_ready` 才能合併。先使用不帶 `--apply` 的預覽，確認檔案與行號正確，再執行：

```bash
python3 <skill-dir>/scripts/merge_translation.py <draft-file> \
  --manifest <manifest-file> \
  --project-root <project-root> \
  --apply
```

合併後執行原始檔驗證：

```bash
python3 <skill-dir>/scripts/validation.py <translation-file>
```

輸出 `NEXT_ACTION=mark_complete` 才能勾選進度。輸出 `worker_continue` 時，清理已合併的 active draft 後再切下一批；輸出 `manager_fix_structure` 時由 manager 修復結構或丟棄並重建該 draft，不要要求 worker 修改來源註解、標頭或工作標記。

驗證失敗時不應把 draft 合併回原始檔，也不應把檔案標成完成。manager 可以使用一般 `diff`／`git diff` 做人工 review，但不能以 diff 取代 `validation.py`。

## progress.md

使用以下腳本初始化或重建檔案清單：

```bash
python3 <skill-dir>/scripts/build_progress.py <scan-path>... \
  --project-root <project-root>
```

它只掃描並列出 `.rpy`，不負責判斷翻譯完成度；重建時會保留既有項目的 `[x]` 狀態，新項目則為 `[ ]`。進度格式保持簡單：

```markdown
# Translation Progress

- [ ] game/tl/tChinese/day1.rpy
- [x] game/tl/tChinese/day2.rpy
```

## translation-guide.md

manager 維護專案根目錄的 `translation-guide.md`。只保留可重複利用且具有長期價值的譯名、術語、角色稱呼、語氣與特殊翻譯決策；若 worker 建議與既有 guide 衝突，保留既有 guide 並在回報中說明。

## 內部工具

- `scripts/build_progress.py`：建立或重建簡單的 progress 清單。
- `scripts/split_translation.py`：依完整翻譯單位建立 draft 與 manifest。
- `scripts/validation.py`：提供 worker-only、draft 完整驗證與原始檔驗證。
- `scripts/merge_translation.py`：依 manifest 將已驗證的工作行範圍回寫原始檔。
- `scripts/translation_units.py`、`scripts/draft_manifest.py`：共用解析與 manifest 型別。

worker 舊有的 `extract.py`、`replace.py` 不屬於新的 draft 流程，不要再把它們設為 worker 的強制步驟；保留它們僅為相容性用途。
