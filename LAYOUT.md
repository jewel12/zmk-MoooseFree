# MoooseFree キーマップレイアウト

`config/MoooseFree.keymap` の各レイヤーをビジュアル化したもの。
キーの左上の小さな数字は `bindings` 配列内のインデックス (combos の `key-positions` で参照する番号)。

## Layer 0 — default

![default_layer](images/layer0_default_layer.svg)

## Layer 1 — ARROW

![ARROW](images/layer1_ARROW.svg)

## Layer 2 — NUM

![NUM](images/layer2_NUM.svg)

## Layer 3 — AHK

![AHK](images/layer3_AHK.svg)

## Layer 4 — FUNCTION

![FUNCTION](images/layer4_FUNCTION.svg)

## Combos

| Name  | Layers | Key positions | Binding      |
|-------|--------|---------------|--------------|
| lang1 | 0      | 51, 52        | `&kp LANG1`  |
| lang2 | all    | 10, 11        | `&kp LANG2`  |

## 凡例

| 表記            | 意味                                                    |
|-----------------|---------------------------------------------------------|
| `Hyp`           | `LC(LS(LA(LG(...))))` (Hyper)                           |
| `Meh`           | `LC(LS(LA(...)))` (Meh)                                 |
| `LS/LC/LA/LG+`  | Shift / Ctrl / Alt / GUI 単独修飾                       |
| `L<n>`          | `&lt <n> <key>` — ホールドでレイヤー n、タップでキー    |
| `L<n>/T0`       | `&lt_to_layer_0 <n> <key>` — ホールドで n、タップで 0   |
| `MO<n>`         | `&mo <n>` — モーメンタリレイヤー切替                    |
| `M:<btn>`       | `&mkp <btn>` — マウスボタン                             |
| `BT<n>`         | `&bt BT_SEL <n>`                                        |
| `BOOT`          | `&bootloader`                                           |
| (空白)          | `&none`                                                 |

## 再生成

```sh
python3 scripts/gen_layout_svgs.py
```
