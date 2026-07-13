# International AI Safety Report 2026 日本語訳プロジェクト

このリポジトリは、[International AI Safety Report 2026](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026)
（原文PDF: `international-ai-safety-report-2026_1.pdf`, 全220ページ）の日本語訳を作成するためのものである。

## 全体方針

1. **全訳ではなく段階的翻訳**。最初に Executive Summary + Extended Summary
   （Key developments since the 2025 Report + Executive summary + Introduction、原文 p.9-15）を翻訳し、
   その内容から本文（Background / Risks / Risk management 等）のうちどこを翻訳すべきか
   （全訳するか、優先度の高い章から進めるか）を検討する。
2. 翻訳は章（Chapter）単位をチャンクとして進める。チャンク分割は `source/` 以下に展開済み
   （`source/_manifest.md` に一覧、詳細は後述）。
3. 出力形式は **HTML**。章ごとに別ファイル＋目次ページ（`html/index.html`）を作成する。
4. **対訳表示（英日並記トグル等）は行わない**。HTMLは日本語訳のみを表示するシンプルな構成とする。
5. **References章（p.157-219、参考文献リスト）はHTML化する**。`html/13_references.html` に各文献番号の
   アンカーを設け、本文中の引用番号からリンクできるようにする。著者名、組織名、論文・資料の正式題名および
   URLは、出典を正確に特定できるよう原文表記を維持する。参考文献ページの見出し・説明は日本語化する。
6. **図表（グラフ・チャート）のキャプション・軸ラベルは本文と同様に翻訳する**。ただし図中の描画部分
   （グラフそのもの）は画像として原文のまま扱い、再作成は行わない。図が本文で言及される際は、
   キャプション・凡例・軸ラベルのテキストを翻訳対象に含める。

## 翻訳ルール（厳守）

- **文体**: である調（常体）。政府・研究機関の公式報告書として、フォーマルな常体で統一する。
- **省略・要約の禁止**: 原文の1文も落とさない。要約・意訳による内容の圧縮は禁止。ただし日本語として
  不自然・破綻する場合は、文の順序や構文を組み替えてよい（文単位の情報を欠落させないことが条件）。
- **正確性を意訳より優先**: 読みやすさのために原文のニュアンスや限定条件（"likely", "may", "some" 等の
  ヘッジ表現）を削ったり強めたりしない。
- **見出し階層・脚注番号は変更しない**: 原文の見出しレベル（H1/H2/H3 …）や章番号（例: §2.1.1）、
  脚注・参考文献番号（例: 827*）はそのまま維持する。原文の番号体系を日本語版でも一致させる。
- **翻訳しないもの**:
  - 参考文献リスト内の著者名、組織名、論文・資料の正式題名、URL
  - 人名
  - 組織名
  - AIモデル名・製品名
  これらは原文（英語表記）のまま記載する。
- **専門用語の表記方針**: `glossary.md` を参照。用語が本文に**初出**する箇所でのみ
  「日本語訳（English term）」の形で英語を併記し、2回目以降は統一された日本語訳のみを用いる。
  本文中に glossary.md 未収録の専門用語が出てきた場合は、翻訳前に glossary.md に追記する。

## 原文PDFの既知の抽出上の不具合（重要・翻訳時に注意）

`scripts/extract_chunks.py` で PDF からテキストを抽出し `source/` 以下に配置しているが、
PDF自体のフォント埋め込みに起因する以下の機械的な文字化けがある（内容の欠落ではない）。
チャンクを翻訳する際は必ず該当箇所を確認し、不審な文字列があれば原文PDFの当該ページ画像と
照合すること。

1. **ピリオドの文字化け**: 文中・文末のピリオド「.」が稀に `�`（U+FFFD）として抽出される。
   `extract_chunks.py` は独立した（連続しない）`�` を自動的に `.` に置換済み。目次ページの
   ドットリーダー（`……` のような連続する `�`）はそのまま残しているが、これらは翻訳対象外の
   ページ（Contents）なので問題にならない。
2. **"AI" → "Al" の誤認識**: p.8（インド代表の寄稿文＝Forewords章の一部）のみ、"AI" が
   "Al"（大文字A + 小文字l）として抽出される。他の全ページでは正常。この1ページを翻訳する際は
   手動で "Al" → "AI" に読み替えること（他の章・References中の "Al-"（アラビア語圏の人名接頭辞、
   例: Al-Dahle, Al-Onaizan）は誤変換ではなく実際の綴りなので触らない）。
3. **単語中の余分なスペース**: 全220ページ中約25ページで、単語の途中に不要なスペースが
   混入することがある（例: "national" → "nationa l"、"such" → "s uch"）。文字の欠落ではなく、
   意味の誤読リスクは低いが、機械的な文字列処理（検索・置換等）を行う場合は注意すること。
4. **脚注の挿入位置ズレ**: PDFの脚注（ページ下部の†や*付き注記）は、抽出テキスト上では
   本文の途中（脚注記号が出現する段落の前後、ページ内の物理的な配置順）に挿入されることがある。
   例: `source/06_introduction.txt` では「systemic risks,†」という本文中の参照より前に
   脚注本文が出現する。翻訳・HTML化の際は、脚注記号の位置と脚注本文を正しく対応づけ、
   HTML では `<sup>` + ページ内リンクや章末注として自然な形に組み直すこと（脚注番号自体は
   変更しない）。

## ディレクトリ構成

- `international-ai-safety-report-2026_1.pdf` — 原文PDF（全220ページ）
- `scripts/extract_chunks.py` — PDFからテキストを抽出し `source/` にチャンク分割するスクリプト
- `source/` — 章・節単位に分割した原文テキスト（英語、クリーニング済み）。`_manifest.md` に一覧。
- `glossary.md` — 統一用語集（英語 / 日本語訳 / 定義）。原典 Glossary 章（p.147-155）の
  全180項目を収録。翻訳作業中に追加の用語が必要になった場合はここに追記する。
- `translations/ja/` — 章ごとの日本語訳（Markdown）。図版は `../../html/images/` へのMarkdown画像リンクとして埋め込む
- `html/` — 最終成果物のHTML（章ごとに1ファイル＋ `index.html` に目次）

## チャンク構成（`source/_manifest.md` より抜粋・翻訳単位）

翻訳の単位は「Top-level」列が "yes" のトップレベル章。トップレベル章の内側にあるサブセクション
ファイル（例: `07a_what_is_general_purpose_ai.txt` 等）は、長い章を分担・並行作業する際の
補助的な分割として用意している。

主なトップレベル章:
1. `00_contributors.txt` — Contributors（人名・組織名のため翻訳対象外、英語のまま）
2. `01_acknowledgements.txt` — Acknowledgements（人名・組織名のため翻訳対象外）
3. `02_forewords.txt` — Forewords（p.8に "Al"→"AI" 誤変換の既知不具合あり）
4. `03_about_this_report.txt` — About this Report
5. `04_key_developments.txt` — Key developments since the 2025 Report
6. `05_executive_summary.txt` — Executive summary
7. `06_introduction.txt` — Introduction
8. `07_background.txt` — Background on general-purpose AI（サブセクション07a-07c）
9. `08_risks.txt` — Risks（サブセクション08a-08c、さらにその下に08a1-08c2）
10. `09_risk_management.txt` — Risk management（サブセクション09a-09e）
11. `10_conclusion.txt` — Conclusion
12. `11_glossary.txt` — Glossary（原文英語のまま。訳語の対応は `glossary.md` を参照）
13. `12_how_to_cite.txt` — How to cite this report（人名・書誌情報のため翻訳対象外）
14. `13_references.txt` — References（`html/13_references.html` にHTML化する。書誌情報は原文表記を維持）
15. `14_colophon.txt` — 奥付（発行者情報。翻訳するかは要検討）

**「Extended Summary」の定義**: このプロジェクトでは `04_key_developments.txt` +
`05_executive_summary.txt` + `06_introduction.txt` の3ファイルをまとめて
「Executive Summary + Extended Summary」の第一弾翻訳対象として扱う。

## 進め方

1. 上記3ファイル（Key developments / Executive summary / Introduction）を翻訳し、
   `translations/ja/` に保存する。
2. 翻訳結果を確認しながら、本文（Background / Risks / Risk management）のうち
   優先的に翻訳すべき章・節を洗い出す。
3. 合意した範囲を章単位で翻訳する。
4. 各章の翻訳が完了次第、`html/` 以下に対応するHTMLファイルを生成し、`html/index.html` の
   目次を更新する。
