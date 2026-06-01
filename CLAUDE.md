# CLAUDE.md

## ファイル構成

- `mf.keymap` — 作業用の最新キーマップ。編集はここで行い、確定したら `config/MoooseFree.keymap` に反映する。
- `config/MoooseFree.keymap` — ZMK ビルドが参照する本体。
- `webapp/index.html` — ブラウザ用キーマップエディタ (単体 HTML)。
- `keyrayout.md` — 物理キー配置 (x, y, w, h, r) の定義。`bindings` 配列のインデックス順。
- `LAYOUT.md` — 各レイヤーを SVG で可視化したドキュメント。
- `images/layer*.svg` — `LAYOUT.md` から参照される SVG。

## キーマップ反映フロー

`mf.keymap` を編集したあと、本体に反映する手順:

```sh
cp mf.keymap config/MoooseFree.keymap
```

## LAYOUT.md / SVG の再生成

`mf.keymap` または `keyrayout.md` を変更したら以下を実行する。`images/layer*.svg` が更新される:

```sh
python3 scripts/gen_layout_svgs.py
```

スクリプトは以下を行う:
- `keyrayout.md` から物理レイアウト (x, y, w, h, r) を読み取る
- `mf.keymap` の `keymap { ... }` ブロックから 5 つのレイヤー (default/ARROW/NUM/AHK/FUNCTION) をパース
- レイヤーごとに `images/layer{N}_{name}.svg` を出力 (回転キー対応、`&none` はグレーアウト)
- キー左上の小さい数字は `bindings` 配列内のインデックス (combos の `key-positions` で参照する値)

ラベルの短縮ルール (`Hyp` = `LC(LS(LA(LG(...))))` など) は `LAYOUT.md` の凡例セクションを参照。
