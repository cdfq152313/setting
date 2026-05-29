---
name: renpy-tl
description: 翻譯 Renpy 為正體中文，並提供翻譯進度管理工具。
---

# 翻譯 Renpy 為正體中文

## 核心規則
1. 不要修改到註解或是字串編號。
2. 保留專有名詞 (如人名、地名等)，不要進行翻譯。
3. 保留 Ren’Py 標籤和變數，例如: {i} {/i} {w=.3} {cps=20} [name] %(value)s
4. 不要調用外部翻譯工具，直接翻譯文本。

## 使用者指定翻譯 .rpy 檔
1. 執行本 skill 內部工具 `scripts/extract.py` 以獲取未翻譯的文本，limit 請不要低於 100 行，以確保翻譯效率。
2. 翻譯後直接取代該行。
3. 若該行不需要翻譯(如僅出現人名、或僅有控制碼等)，請在該行行尾添加註解 `# i18n: skip`。範例如下
    ```rpy
    new "Harry" # i18n: skip
    ```
4. 重複上述步驟直到整個檔案翻譯完成。

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


## Skill 內部工具

### `scripts/extract.py` — 提取未翻譯文本

用法如下
```
python3 <skill-dir>/scripts/extract.py <current-file> --limit 100
```

重點提要:
- <skill-dir> 是包含此 `SKILL.md` 的目錄
- `<current-file>` 是當前正在翻譯的 `.rpy` 文件的路徑。
- `--limit` 參數指定要提取的未翻譯文本行的最大數量。

輸出格式為 `行號: 文本`，其中行號為原始 `.rpy` 文件中的行號，文本為該行的內容。範例如下:

```
7: MC "I think I'll go ahead and read some of the book I got from Coach."
13: MC "Let's see here. Chapter one..."
28: new "Harry"
```
