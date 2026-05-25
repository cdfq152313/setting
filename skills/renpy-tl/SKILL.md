---
name: renpy-tl
description: 翻譯 Renpy 為正體中文，並提供翻譯進度管理工具。
---

# 翻譯 Renpy 為正體中文

## 核心規則
1. 不要修改到註解或是字串編號。
2. 專有名詞 (如人名) 請保留，不要進行翻譯。
3. 不要調用外部翻譯工具，直接翻譯文本。

## 使用者指定翻譯 .rpy 檔
1. 執行 skill script `scripts/check.py`（使用 `--short`）找到第一行尚未翻譯的位置，從該位置續翻。
2. 一次翻譯 1000 行（請自行處理邊界問題），完成後回到步驟 1 繼續翻譯下一批行，直到整份檔案翻譯完成。
3. 忽略註釋行號，註釋行號必定非實際行號。
4. 檔案翻譯完成後，執行 skill script `scripts/check.py` 確認是否仍有未翻譯的行。
5. 直到檔案翻譯完成才停止，禁止翻譯一個區塊就停止。

## 使用者指定翻譯自進度檔

若使用者指定進度檔`batch-xxx.md` 則

1. 讀取進度檔，找到第一個未完成的檔案開始翻譯。
2. 請逐檔翻譯，不要一次翻譯多個檔案。
3. 翻譯步驟同上方`使用者指定翻譯 .rpy 檔`。
4. 當整份檔案翻譯完成後，將進度檔標記為已完成。

## 專案初始化
當使用者要求初始化翻譯進度時：
1. 掃描使用者指定的範圍內的 `.rpy`
2. 創建指定數量的 `progress/batch-xxx.md` 進度表。
3. 將每個發現的 `.rpy` 文件分配給一個批次，盡可能平衡估計的翻譯工作量。

## 進度檔格式

進度檔 `batch-xxx.md` 的格式如下：

```markdown
# Translation Progress: batch-001

- [x] game/day1.rpy
- [ ] game/day2.rpy
```


## Available scripts

### `scripts/check.py` — 檢查翻譯完成度

執行:

```bash
python3 scripts/check.py <current-file> --proper-nouns-file <project-root>/names.txt` --short
```

用法:
- `<project-root>` 是目標 Ren'Py 專案根目錄
- `names.txt` 是專案根目錄下的換行分隔的專有名詞允許列表文件，每行一個名稱，並可選擇性地包含 `#` 注釋。
    - 如果 `names.txt` 不存在，工具應該創建一個空文件並繼續運行。
    - 如果未解決的候選詞是應保持不翻譯的專有名詞，僅將這些專有名詞附加到 `<project-root>/names.txt`，然後重新運行檢查器。
- `--short` 選項將輸出統計摘要，最多顯示前 5 條未翻譯的項目。
