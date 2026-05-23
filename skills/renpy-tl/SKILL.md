---
name: renpy-tl
description: Translate and revise Ren'Py `.rpy` localization files into Traditional Chinese.
---

# Ren'Py Traditional Chinese Translation

## Hard Rules

1. Translate target user-facing text into Traditional Chinese.
2. Preserve proper nouns such as character and place names in their original form unless the user provides an explicit approved translation or glossary.
3. Preserve all Ren'Py/Python syntax and inline tokens exactly, including `[name]`, `{w=.3}`, `{i}`, `{color=#...}`, `{#...}`, escaped braces, interpolation, and embedded Python expressions.
4. Translate directly from the provided text. Do not call external translation tools or translation services.

## Editing Procedure

1. In ordinary `translate <language> <id>:` dialogue blocks, leave the `#` source line untouched and translate only the corresponding uncommented dialogue string.
2. In `translate <language> strings:` blocks, leave each `old` value untouched and translate only the matching `new` value.
3. Before finishing, verify that only target translation strings changed.

## Translation Chunk Size

1. For dialogue or scene translation, process one coherent scene or up to 50 target strings per translation chunk, whichever comes first.
2. For short UI or system-text entries in `translate ... strings:` blocks, process up to 100 `new` values per translation chunk.
3. A translation chunk is an internal progress unit, not a stopping point that requires user confirmation.

## Progress Modes

### Initialize Progress

When the user asks to initialize translation progress:

1. Scan the user-specified scope for target `.rpy` files.
2. Create the requested number of `progress/batch-xxx.md` files.
3. Assign every discovered `.rpy` file to exactly one batch, balancing estimated translation work when practical.
4. Include one progress-table row per assigned file, with `Status` set to `not started` and `Resume Point` set to `line 1`.
5. During initialization, create or edit only progress files. Do not translate or modify `.rpy` files.

### Translate From Progress

When the user asks to translate a `progress/batch-xxx.md` file:

1. Read the specified batch file and edit only its assigned `.rpy` files and that batch file.
2. Repeatedly translate the next unfinished translation chunk according to the translation chunk-size rules above.
3. After each completed chunk, update the batch file row for the current `.rpy` file:
   - Set `Status` to `in progress`.
   - Set `Resume Point` to `line N`, where `N` is the next physical line to inspect.
4. After completing all target strings in an assigned `.rpy` file, set its `Status` to `completed` and its `Resume Point` to `completed`, then continue with the next unfinished assigned file.
5. Do not pause to ask whether to continue after completing a chunk or a file.
6. Stop only when all assigned files are completed, the user requests a stop, a blocking ambiguity requires user input, or execution limits prevent continuing safely.
7. When stopping before the batch is complete, ensure the latest completed chunk has been recorded in the batch file and report the next resume point in the same format, such as `line 240`.
8. Do not edit files or progress records assigned to another batch.

### Batch File Format

Use this format for each `progress/batch-xxx.md` file:

````markdown
# Translation Progress: batch-001

## Assigned Files

| Status | File | Resume Point |
| --- | --- | --- |
| not started | `game/day1.rpy` | line 1 |
| in progress | `game/day2.rpy` | line 240 |
| completed | `game/day3.rpy` | completed |
````

Each assigned `.rpy` file must have exactly one row.

### Progress Status Rules

Use exactly one of these status values for each assigned file:

- `not started`: no target strings in this file have been translated yet. Set `Resume Point` to `line 1`.
- `in progress`: some target strings have been translated, but the file is not complete. Set `Resume Point` to the next physical line number to inspect, formatted as `line N`.
- `completed`: all target strings in this file have been translated. Set `Resume Point` to `completed`.

Line numbers are 1-based physical file line numbers, matching `nl -ba <file>`. After each completed translation chunk, update the progress file so the resume point is the first line after the last safely completed translated block.

## Examples

### Dialogue Translation Block

Translate only the final uncommented string. Keep `Cole`, the source comment, the label, and `{w=.3}` unchanged.

```renpy
# game/mini_episodes/MFF_build.rpy:9
translate Schinese episode_MFF_ca744f3e:

    # "Usually being surrounded by half-naked men was more exciting than this,{w=.3} Cole mused."
    "通常被一群半裸的男人圍著應該比現在更刺激才對，{w=.3} Cole 心想。"
```

### String Table

Translate only `new`. Keep `old` and the location comment unchanged.

```renpy
translate tChinese strings:

    # game/day1.rpy:281
    old "Huh? That's not my name."
    new "咦？那不是我的名字。"
```
