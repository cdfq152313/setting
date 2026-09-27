---
name: renpy-tl-worker
description: 翻譯 manager 指定的單一 Ren'Py draft，並在不改動上下文與結構的前提下完成工作範圍。當使用者或 manager 要求處理一份 draft 時使用；不要用於專案排程、原始檔合併或多檔案調度。
---

# Ren'Py 翻譯 worker

## 工作邊界

一次只處理 manager 指定的一份 `.rpy` draft。工作期間只可閱讀：

1. 該份 draft；
2. 專案根目錄的 `translation-guide.md`（若存在）。

不得閱讀原始翻譯檔、其他 `.rpy`、`progress.md`、manifest 或其他專案檔案來補充上下文。draft 已包含 manager 指定數量的已翻譯上下文；不要因為想取得更多背景而擴大讀取範圍。

不要修改原始檔、progress 或 guide。不要直接翻譯整個專案，也不要同時處理另一個檔案。

## 工作流程

1. 先閱讀指定 draft；若 manager 提供 `translation-guide.md`，先閱讀它。
2. 找到唯一一對 `# renpy-tl-draft: work-begin` 與 `# renpy-tl-draft: work-end`。標記外的內容是唯讀上下文，包含已翻譯單位、來源位置註解、`translate` 標頭與空白行。
3. 只翻譯兩個標記之間的完整未翻譯單位。不要移動、刪除或修改兩個標記，也不要在 draft 中加入自己的註解或額外分隔線。
4. 完成後使用 manager skill 提供的只讀 draft 驗證：

   ```bash
   python3 <manager-skill-dir>/scripts/validation.py <draft-file> --worker
   ```

   這個命令只讀 draft，不需要原始檔或 manifest。輸出 `NEXT_ACTION=worker_continue` 就繼續翻譯；輸出 `NEXT_ACTION=worker_done` 才回報 manager；輸出 `NEXT_ACTION=manager_fix_structure` 時不要修復標記或結構，直接回報 manager。

## 翻譯與結構規則

- 使用自然、流暢的正體中文，遵守 guide 中的譯名、稱呼、角色語氣與術語。
- 保留原有專有名詞，除非 guide 或既有上下文指定譯法。
- 保留 Ren'Py tag 與 placeholder，例如 `{i}`、`{/i}`、`{w=.3}`、`{cps=20}`、`[name]`、`%(value)s`；不可遺失、增加或改變其內容。
- 保留引號、跳脫字元、縮排與每個翻譯單位的實體行數。不要把一行拆成多行，也不要把多行合併成一行。
- 一般對話單位只修改翻譯文字行；不要修改來源註解、`translate` 標頭、字串 ID 或其他結構。
- `translate ... strings:` 單位只修改對應的 `new` 文字；保留 `old`、來源位置註解與區塊結構。
- 如果內容刻意維持原文，例如只有人名或只有不應翻譯的控制內容，在工作範圍內的目標文字行尾加入 `# i18n: skip`。不要為其他理由加入註解。
- 不要呼叫外部翻譯工具，不要根據未讀取的專案內容自行補充設定。

## 完成回報

回報以下內容：

1. 處理完成的 draft 路徑；
2. `validation.py --worker` 的結果，是否為 `NEXT_ACTION=worker_done`；
3. 尚未完成或無法判斷的單位（若有）；
4. 建議加入 `translation-guide.md` 的長期資訊；若沒有則寫「無」。

不要自行把 draft 合併回原始檔，也不要修改 progress。manager 會執行需要 manifest 與原始檔的完整驗證、合併及進度更新。

## 交接回報

若 manager 要求交接後關閉，回報：

1. 目前處理的 draft 路徑；
2. 尚未完成的工作範圍或疑難單位；
3. 角色稱呼、術語、語氣或上下文決策；
4. 建議加入 guide 的項目；若沒有則寫「無」。

舊有的 `extract.py`、`replace.py` 是原始檔直接編輯流程的相容性工具，不是目前 draft 工作的必要步驟。
