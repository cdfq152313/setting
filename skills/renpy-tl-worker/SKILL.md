---
name: renpy-tl-worker
description: 將單一 Ren'Py 翻譯檔中的未翻譯文本翻成正體中文，並安全回寫指定行。當使用者要求翻譯單個 .rpy 檔、處理 manager 分派的檔案、保留 Ren'Py 標籤與變數、或需要檢查與回寫未翻譯行時使用。不要用於專案層級的進度安排或多檔案調度。
---

# 翻譯單一 Ren'Py 檔案

## 核心規則

1. 不要修改註解、字串編號、`translate` 區塊標頭，或任何與翻譯無關的結構。
2. 保留專有名詞，例如人名、地名、組織名；不要擅自翻譯。
3. 保留 Ren'Py 標籤和變數，例如 `{i}` `{/i}` `{w=.3}` `{cps=20}` `[name]` `%(value)s`。
4. 不要調用外部翻譯工具；直接翻譯文本。
5. 一次只處理單一 `.rpy` 檔案；若任務是整個專案的排程，交由 `$renpy-tl-manager` 負責。

## 工作流程

1. 若專案根目錄存在 `translation-guide.md`，先閱讀該檔案。
2. 執行 `scripts/extract.py` 擷取未翻譯文本。`--limit` 不要低於 100，以維持翻譯效率。
3. 逐行翻譯抽出的文本，並直接回寫到原始 `.rpy` 對應行。
4. 若某行不需要翻譯，例如只有人名或只有控制碼，則在該行行尾加入 `# i18n: skip`。
5. 重複抽取與回寫，直到 `scripts/extract.py` 已無輸出。
6. 結束前再用 `--limit 100` 重新檢查一次，確認該檔案已無待翻譯內容。

## 跳過不需翻譯的行

範例：

```rpy
new "Harry" # i18n: skip
```

## 上下文理解

1. 翻譯前應閱讀待翻譯行附近內容，以理解說話者、對象、語氣與劇情上下文。
2. 預設閱讀待翻譯行前後約 20 行；若遇到代名詞、曖昧指稱、雙關語或依賴劇情理解的內容，可擴大閱讀範圍。
3. 除非原文明確如此，避免無根據地增加、刪減或改寫語意。

## 一致性來源

1. 若專案根目錄存在 `translation-guide.md`，翻譯前必須先閱讀。
2. `translation-guide.md` 內的譯名、稱呼、角色語氣與常用句優先於自行判斷。
3. 不要為了一致性而掃描整個專案或大量舊翻譯；worker 只需參考：
   - `translation-guide.md`
   - 目前 `.rpy` 檔案附近上下文
4. 若 guide 沒有記載，依目前檔案上下文翻譯。
5. 若發現反覆出現但 guide 未記載的重要譯名、術語、角色稱呼或語氣規則，結束時在回報中列出，不要擅自修改 `translation-guide.md`。

## 翻譯風格

1. 使用自然、流暢的正體中文。
2. 優先維持角色語氣、稱呼方式與情緒強度。
3. 相同原文在相同語境下應盡量使用相同譯法。
4. 不確定時，優先保守直譯，不要自行補充世界觀設定或角色背景。

## 完成回報

結束時回報：

1. 已完成的 `.rpy` 檔案。
2. 是否已用 `scripts/extract.py --limit 100` 確認無待翻譯內容。
3. 建議加入 `translation-guide.md` 的項目；若沒有則寫「無」。

## 交接回報

若 manager 要求交接後關閉，回報：

1. 目前處理的 `.rpy` 檔案。
2. 建議加入 `translation-guide.md` 的項目；若沒有則寫「無」。
3. 新 worker 需要注意的角色稱呼、術語、語氣或上下文決策。

## 內部工具

### `scripts/extract.py`

提取未翻譯文本。

用法：

```bash
python3 <skill-dir>/scripts/extract.py <current-file> --limit 100
```

輸出格式：

```text
7: MC "I think I'll go ahead and read some of the book I got from Coach."
13: MC "Let's see here. Chapter one..."
28: new "Harry"
```
