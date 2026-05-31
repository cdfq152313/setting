---
name: renpy-tl-manager
description: 管理 Ren'Py 正體中文翻譯專案的進度檔、檔案分派與完成度驗收。當使用者要求初始化 progress.md、依進度檔安排翻譯順序、將多個 .rpy 分派給子代理、檢查哪些檔案尚未完成，或在整個專案層級追蹤翻譯進度時使用。
---

# 管理 Ren'Py 翻譯進度

## 核心職責

1. 初始化或重建 `<project-root>/progress.md`。
2. 從進度檔挑出尚未完成的 `.rpy`，依序安排翻譯。
3. 將單一檔案工作分派給 `$renpy-tl-worker` 子代理。
4. 使用驗證腳本驗收檔案是否可標記完成，包含未翻譯文本與結構檢查。

## 管理規則

1. 不要直接翻譯文本；manager 只負責安排、驗收與更新進度。
2. 依 `progress.md` 的順序，由上而下處理未完成項目。
3. 每個子代理一次只處理一個 `.rpy` 檔案，並明確要求使用 `$renpy-tl-worker`。
4. 若使用者沒有指定子代理數量，預設同時啟用最多 2 個子代理。
5. 若使用者沒有指定要翻譯多少個檔案，預設只處理 2 個尚未完成的檔案。
6. 子代理一旦回報完成，主代理必須立刻 review 與驗收該檔案，不要等待其他子代理全部結束。
7. 只有在驗收確認檔案已完成後，才能將 `progress.md` 對應項目標記為 `[x]`。
8. 驗收失敗時，該檔案不得標記為完成，也不得改派其他檔案；必須依驗收結果處理同一檔案。
9. 一個子代理完成並通過驗收後，就關閉該子代理；不要重複利用同一個子代理去接下一個檔案。

## Translation Guide 管理

1. 若專案根目錄存在 `translation-guide.md`，分派子代理時必須告知 worker 先讀取該檔。
2. manager 負責維護 `translation-guide.md`；worker 不得自行修改。
3. 子代理回報「建議加入 translation-guide.md 的項目」時，manager 應在驗收通過後統一 review。
4. 可加入任何能提升後續翻譯一致性與正確性的資訊，例如：
   - 譯名與術語
   - 角色稱呼與語氣
   - 人物關係
   - 劇情設定
   - 世界觀資訊
   - 特殊翻譯決策
5. 僅記錄可重複利用且具有長期價值的資訊；不要記錄單次場景或一次性的劇情細節。
6. 若建議項目與既有 guide 衝突，保留既有 guide，並在回報中列出衝突。
7. translation-guide.md 的格式不需預先固定；manager 應根據內容自行整理為清晰、易讀且便於後續維護的結構。

## 子代理輪替與交接

1. 本節只適用於驗收結果為 `NEXT_ACTION=worker_continue` 的情況。
2. 初次分派不計入「繼續」次數；每次驗收結果為 `NEXT_ACTION=worker_continue` 並要求同一子代理繼續時，該檔案的繼續次數加 1。
3. 同一子代理在同一檔案上最多繼續 2 次；若第 2 次繼續後仍未完成，manager 必須要求該子代理回報交接資訊，再關閉它。
4. 交接資訊必須包含：
   - 目前處理的 `.rpy` 檔案
   - 建議加入 `translation-guide.md` 的項目；若沒有則寫「無」
   - 新子代理需要注意的角色稱呼、術語、語氣或上下文決策
5. worker 不得自行修改 `translation-guide.md`；manager review 交接資訊後，僅將具長期價值的項目寫入 guide。
6. 重開子代理不代表該檔案失敗；新子代理必須重新讀取 `translation-guide.md`，依 `$renpy-tl-worker` 工作流程重新執行 `extract.py`，並從目前檔案狀態繼續處理同一檔案。

## 初始化進度檔

使用 `scripts/build_progress.py` 掃描指定範圍內的 `.rpy`，並建立 `<project-root>/progress.md`。

用法：

```bash
python3 <skill-dir>/scripts/build_progress.py <scan-path>... --project-root <project-root>
```

重點：
- `<scan-path>` 可以是單一 `.rpy`、資料夾，或多個混合輸入。
- `progress.md` 預設寫到 `<project-root>/progress.md`。
- 進度檔中的路徑必須使用相對於 `<project-root>` 的相對路徑。

## 依進度檔分派工作

1. 讀取 `<project-root>/progress.md`，找出所有 `- [ ]` 項目。
2. 依管理規則決定本輪要處理的檔案數量與同時啟用的子代理數量。
3. 取出本輪目標檔案，並只保留最前面的指定數量。
4. 初始派出 `min(子代理數量, 本輪檔案數量)` 個子代理，將本輪檔案依序分配出去。
5. 每個子代理的提示都必須包含：
    - 只能處理被分配的單一檔案
    - 必須使用 `$renpy-tl-worker`
    - 若存在 `translation-guide.md`，必須先讀取
    - 不得修改 `progress.md`
    - 不得修改 `translation-guide.md`
    - 依 `$renpy-tl-worker` 工作流程執行 `extract.py` 時，`--limit` 不得低於 100
    - 完成後立即回報
6. 子代理模型固定使用 `gpt-5.4-mini (Reasoning low)`，除非使用者明確要求其他配置。
7. 當任一子代理回報完成時，立刻執行驗收流程。
8. 若驗收結果為 `NEXT_ACTION=manager_fix_structure`，manager 修復結構問題並關閉造成該結果的 worker；修復後重新驗收同一檔案。
9. 若驗收結果為 `NEXT_ACTION=worker_continue`，依「子代理輪替與交接」處理同一檔案，不要用下一個檔案取代它；要求同一 worker 繼續時，續工提示只說明仍有未翻譯文本。
10. 若驗收結果為 `NEXT_ACTION=mark_complete`，立即更新 `progress.md`、關閉該子代理，並在仍有剩餘待處理檔案時新開下一個子代理補上空缺。
11. 重複上述節奏，直到本輪指定檔案全部驗收完成為止。

## 驗收流程

完成單一檔案後，使用本 skill 內的 `scripts/validation.py` 驗收：

```bash
python3 <skill-dir>/scripts/validation.py <project-root>/<relative-file> --git-base HEAD
```

規則：
- `NEXT_ACTION=mark_complete`：才可將該檔案標記為完成。
- `NEXT_ACTION=worker_continue`：仍有未翻譯文本；不要勾選 `[x]`，而是讓同一檔案繼續翻譯。
- `NEXT_ACTION=manager_fix_structure`：manager 先修復結構問題，關閉造成該結果的 worker，修復後重新執行 `validation.py`。
- 若 `validation.py` 回報 `NEXT_ACTION=manager_fix_structure`，但檢視對應行後確認內容正確，停止派發新的 worker，不要標記完成或要求 worker 修正；立即回報疑似 false positive、檔案、錯誤類型與行號，等待使用者決定。
- 每次處理完 `validation.py` 指示的動作後，都必須重新執行 `validation.py`；只有 `NEXT_ACTION=mark_complete` 可以更新 `progress.md`。
- 驗收通過後要立刻更新 `progress.md`，不要等到整批檔案都完成才一起更新。
- 驗收通過後，若子代理回報了建議加入 `translation-guide.md` 的項目，manager 應 review 並視情況更新 guide。

## 調度範例

使用者要求 2 個子代理處理 4 個檔案時，流程如下：

1. 主代理先派出 2 個子代理，各自處理第 1 與第 2 個檔案。
2. 其中任一子代理先回報完成時，主代理立刻 review 並驗收該檔案。
3. 若驗收成功，主代理立刻更新 `progress.md`，關閉該子代理，然後新開下一個子代理去處理第 3 個檔案。
4. 之後每次有子代理完成，就重複「立刻驗收、立刻更新進度、關閉該子代理、再新開下一個子代理」的節奏。
5. 全部 4 個檔案都完成驗收後才結束。

## 進度檔格式

```markdown
# Translation Progress

- [x] game/day1.rpy
- [ ] game/day2.rpy
```

## 內部工具

### `scripts/build_progress.py`

掃描 `.rpy` 並建立或重建 `progress.md`。

### `scripts/validation.py`

驗收單一 `.rpy`。輸出 `NEXT_ACTION` 與各類問題行號；只有 `NEXT_ACTION=mark_complete` 代表可勾選進度。
