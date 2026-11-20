# International AI Safety Report 2026 日本語訳プロジェクト

このリポジトリは、[International AI Safety Report 2026](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026)
（原文PDF: `international-ai-safety-report-2026_1.pdf`, 全220ページ）の日本語訳を作成するためのものである。

本報告書は毎年改訂版が発行されるシリーズである。次年度版（2027年版）が出た際は、本ファイルに
記載された規則・パイプラインをそのまま適用して処理できることを意図している。新しい原文PDFに
差し替えて `scripts/extract_chunks.py` を再実行するところから始めること。ページ番号や章構成が
変わっている場合は `source/_manifest.md` や本ファイルの章リストを合わせて更新する。

## 全体方針

1. **全訳を目指す。** 本プロジェクトは Executive Summary + Extended Summary
   （Key developments since the 2025 Report + Executive summary + Introduction、原文 p.9-15）から
   着手し、その後 Background / Risks / Risk management の全節、Forewords、About this Report、
   Conclusion、Contributors、Acknowledgements、How to cite this report、Colophon と範囲を広げて
   最終的に全訳している（Glossary は原文英語のまま、訳語対応は `glossary.md` を参照。References は
   書誌情報を原文表記のまま HTML 化。詳細は下記「翻訳対象外のもの」を参照）。次年度版でも同様に
   全訳を目指す。
2. 翻訳は章（Chapter）単位をチャンクとして進める。チャンク分割は `source/` 以下に展開済み
   （`source/_manifest.md` に一覧、詳細は後述）。
3. 出力形式は **HTML**。章ごとに別ファイル＋目次ページ（`docs/index.html`）を作成する。
   出力先ディレクトリは `docs/`（GitHub Pages が `docs/` から配信される設定になっている。
   かつては `html/` だったが移行済み。新しいスクリプトや手順書で `html/` という表記を見かけたら
   誤りなので `docs/` に読み替える）。
4. **対訳表示（英日並記トグル等）は行わない**。HTMLは日本語訳のみを表示するシンプルな構成とする。
5. **References章（p.157-219、参考文献リスト）はHTML化する**。`docs/13_references.html` に
   各文献番号のアンカー（`id="ref-N"`）を設ける。著者名、組織名、論文・資料の正式題名および
   URLは、出典を正確に特定できるよう原文表記を維持する。参考文献ページの見出し・説明文は
   日本語化する。**本文中の引用番号（例: `(55)`, `(1149*)`）はクリック可能なリンクに変換するが、
   これはビルド時に静的生成するのではなく `docs/citation-links.js` がページ読み込み時に
   クライアントサイドで行う**（仕組みは後述「参考文献リンクの仕組み」を参照）。したがって
   翻訳Markdown中の引用番号は、通常の文章として普通に括弧書きするだけでよく、Markdownリンク
   記法 `[55](...)` 等に変換する必要はない（むしろしてはいけない。citation-links.js が正しく
   認識できなくなる）。
6. **図表（グラフ・チャート）のキャプション・軸ラベルは本文と同様に翻訳する**。ただし図中の描画部分
   （グラフそのもの）は画像として原文のまま扱い、再作成は行わない。図が本文で言及される際は、
   キャプション・凡例・軸ラベルのテキストを翻訳対象に含める。画像の切り出し方法は後述
   「図版の抽出」を参照。

## 翻訳ルール（厳守）

- **文体**: である調（常体）。政府・研究機関の公式報告書として、フォーマルな常体で統一する。
- **省略・要約の禁止**: 原文の1文も落とさない。要約・意訳による内容の圧縮は禁止。ただし日本語として
  不自然・破綻する場合は、文の順序や構文を組み替えてよい（文単位の情報を欠落させないことが条件）。
- **正確性を意訳より優先**: 読みやすさのために原文のニュアンスや限定条件（"likely", "may", "some" 等の
  ヘッジ表現）を削ったり強めたりしない。
- **見出し階層・脚注番号は変更しない**: 原文の見出しレベル（H1/H2/H3 …）や章番号（例: §2.1.1）、
  脚注・参考文献番号（例: 827*）はそのまま維持する。原文の番号体系を日本語版でも一致させる。
  引用番号末尾の `*`（例: `64*`）は原文報告書自身の脚注規則で「産業界に関係する参考文献
  （industry-affiliated reference）：営利AI企業が発表した論文、または著者の過半数がそうした
  企業に所属する論文」を示す記号であり（`source/13_references.txt` 冒頭に定義あり）、改変・削除
  しないこと。この `*` は Markdown のイタリック記号と衝突しやすいので、HTML生成時の扱いに注意
  （後述「Markdown記法の規約」のイタリックの項を参照）。
- **翻訳しないもの（原文＝英語表記のまま記載する）**:
  - 人名
  - 組織名・機関名（例: OECD, EU, UN のような略称はそのまま。正式名称を併記する場合は
    「日本語訳（英語略称）」の順、例: 「欧州連合（EU）」）
  - AIモデル名・製品名
  - 参考文献リスト内の著者名、論文・資料の正式題名、URL
  - BibTeXエントリ等の書誌データそのもの（`12_how_to_cite.md` 参照）
  - 国名は上記の「組織名」には含まれない。**国名は日本語に翻訳する**（例: Australia → オーストラリア、
    the Republic of Korea → 大韓民国）。Contributors の専門家諮問委員会メンバー国リスト等で
    前例あり。
- **専門用語の表記方針**: `glossary.md` を参照。用語が本文に**初出**する箇所でのみ
  「日本語訳（English term）」の形で英語を併記し、2回目以降は統一された日本語訳のみを用いる。
  本文中に glossary.md 未収録の専門用語が出てきた場合は、翻訳前に glossary.md に追記する
  （`scripts/build_glossary.py` と `scripts/glossary_translations.py` / `glossary_supplementary.py`
  を参照。前者は原文 Glossary 章 180 項目を機械的に整形するスクリプトで、後者2つが実際の
  日本語訳と、Glossary章に無いが本文中で補った補助項目を保持する）。

### Anthropic Usage Policy に抵触する記載の扱い

原文には、ごく一部（例: §3.3 Table 3.8 のジェイルブレイク手法の実例）に、爆発物の自作手順や
違法行為の具体的手順など、そのまま翻訳・掲載するとAnthropic社のUsage Policyに抵触する内容が
含まれる。このような箇所が見つかった場合：

1. **ブロックする／回避することが目的ではない。** まず該当箇所を行・セル単位に細分化し、
   どの具体的な記述が問題なのかを正確に特定すること（表全体や節全体を一括で「未記載」にしない）。
2. 問題となる記述以外（分類・タクソノミー、プロンプトの構造、引用番号、表の体裁等）は**通常通りすべて翻訳する**。
3. 問題となる記述そのものだけを、内容の性質を示す中立的・説明的な記述に置き換える
   （例: 「安全対策を回避した場合の、当該要求に準拠する出力例。」）。
4. 置き換えた箇所の直後に、**具体的に何を・なぜ記載しなかったかを明示する注記**を置く。
   「記載できない」という抽象的な説明だけで済ませない。実例は
   `translations/ja/09c_technical_safeguards_monitoring.md` の `<div class="aup-note">...</div>` を参照。
   このdivはMarkdown中に生HTMLとしてそのまま埋め込んでよく、`scripts/generate_docs.py` が
   パススルーする（後述）。
5. `docs/index.html` の目次で該当節に `<span class="badge partial">一部未記載（Usage Policy）</span>`
   バッジを付け、目次下部の `.notice` に一文で補足する。

## 原文PDFの既知の抽出上の不具合（重要・翻訳時に注意）

`scripts/extract_chunks.py` で PDF からテキストを抽出し `source/` 以下に配置しているが、
PDF自体のフォント埋め込みに起因する以下の機械的な文字化けがある（内容の欠落ではない）。
チャンクを翻訳する際は必ず該当箇所を確認し、不審な文字列があれば原文PDFの当該ページ画像と
照合すること。次年度版PDFでも同種の文字化けが起こりうるので、同じ観点でチェックすること。

1. **ピリオドの文字化け**: 文中・文末のピリオド「.」が稀に `�`（U+FFFD）として抽出される。
   `extract_chunks.py` は独立した（連続しない）`�` を自動的に `.` に置換済み。目次ページの
   ドットリーダー（`……` のような連続する `�`）はそのまま残しているが、これらは翻訳対象外の
   ページ（Contents。`01_acknowledgements.txt` 後半に同梱されている。詳細は後述）なので
   問題にならない。
2. **"AI" → "Al" の誤認識**: p.8（インド代表の寄稿文＝Forewords章の一部）のみ、"AI" が
   "Al"（大文字A + 小文字l）として抽出される。他の全ページでは正常。この1ページを翻訳する際は
   手動で "Al" → "AI" に読み替えること（他の章・References中の "Al-"（アラビア語圏の人名接頭辞、
   例: Al-Dahle, Al-Onaizan）は誤変換ではなく実際の綴りなので触らない）。次年度版では該当ページ
   番号が変わる可能性があるので、Forewords章を抽出・翻訳する際に毎回目視確認すること。
3. **単語中の余分なスペース**: 全220ページ中約25ページで、単語の途中に不要なスペースが
   混入することがある（例: "national" → "nationa l"、"such" → "s uch"）。文字の欠落ではなく、
   意味の誤読リスクは低いが、機械的な文字列処理（検索・置換等）を行う場合は注意すること。
4. **脚注の挿入位置ズレ**: PDFの脚注（ページ下部の†や*付き注記）は、抽出テキスト上では
   本文の途中（脚注記号が出現する段落の前後、ページ内の物理的な配置順）に挿入されることがある。
   例: `source/06_introduction.txt` では「systemic risks,†」という本文中の参照より前に
   脚注本文が出現する。翻訳時はMarkdown中では脚注記号 `†` を参照箇所にそのまま書き、脚注本文は
   別パラグラフとして `† 本文...` の形で（原文の抽出順通りの位置でよい）書けば、
   `scripts/generate_docs.py` が自動的に `<sup id="fnref-N"><a href="#fn-N">†</a></sup>` と
   ページ末の脚注リストに組み直す（詳細は後述「Markdown記法の規約」）。脚注番号自体（†や*）は
   変更しない。

## ディレクトリ構成

- `international-ai-safety-report-2026_1.pdf` — 原文PDF（全220ページ）。次年度版が出たら
  このファイルを差し替える（ファイル名は変更しない方が各スクリプトの参照が楽）。
- `scripts/extract_chunks.py` — PDFからテキストを抽出し `source/` にチャンク分割するスクリプト
- `scripts/extract_figures.py` — PDFから図版（グラフ・チャート）を画像として切り出し
  `docs/images/` に保存するスクリプト。詳細は後述「図版の抽出」。実行には `pymupdf`
  パッケージが必要（`pip install pymupdf`）。このコンテナでは `python3` ではなく
  `python3.13` にのみインストール済みの場合があるため、`fitz`/`pymupdf` の import に
  失敗したら `python3.13 -m pip install pymupdf` ないし `which python3.13` を確認すること。
- `scripts/embed_figures_in_markdown.js` — （過去に一括変換で使った補助スクリプト）
  `**[図: Figure X.X]** — 説明（画像: \`html/images/fig_N.png\`）` という旧式の図版プレースホルダ
  記法を、現行の `![Figure X.X: 説明](../../docs/images/fig_N.png)` というMarkdown画像記法に
  変換する。**現在は新規翻訳で旧式プレースホルダを使っていないため、通常は不要**（最初から
  `![Figure X.X: 説明](...)` 形式で書く。後述「Markdown記法の規約」参照）。過去の変換結果との
  互換性のために残してある。
- `scripts/build_references_html.js` — `source/13_references.txt` を解析し、
  `docs/13_references.html`（参考文献ページ、`id="ref-N"` アンカー付き）を生成する Node スクリプト。
  併せて `docs/` 以下の各章HTMLに `<script src="citation-links.js"></script>` タグが
  付いているか確認し、無ければ追加する（`scripts/generate_docs.py` が既に付けているので通常は
  no-op）。参考文献数が変わった場合に備えて件数チェック（現状1451件）が入っているので、
  次年度版で参考文献数が変わったらこの数値も更新すること。
- `scripts/build_glossary.py` / `scripts/glossary_translations.py` /
  `scripts/glossary_supplementary.py` — 原文 Glossary 章（`source/11_glossary.txt`）と
  日本語訳の対応表から `glossary.md` を生成するスクリプト群。
- `scripts/generate_docs.py` — `translations/ja/*.md` から `docs/*.html` の章ページを生成する
  メインのビルドスクリプト。詳細は後述「HTML生成パイプライン」。
- `source/` — 章・節単位に分割した原文テキスト（英語、クリーニング済み）。`_manifest.md` に一覧。
- `glossary.md` — 統一用語集（英語 / 日本語訳 / 定義）。原典 Glossary 章（p.147-155）の
  全180項目＋本文翻訳中に追加した補助項目を収録。翻訳作業中に追加の用語が必要になった場合は
  ここに追記する。
- `translations/ja/` — 章ごとの日本語訳（Markdown）。記法の詳細は後述「Markdown記法の規約」。
- `docs/` — 最終成果物のHTML（GitHub Pages 配信元）。
  - `docs/index.html` — 目次ページ
  - `docs/13_references.html` — 参考文献ページ（`build_references_html.js` が生成）
  - `docs/style.css` — 全ページ共通のスタイルシート。章ページ・目次・参考文献ページすべてが
    これを `<link rel="stylesheet" href="style.css">` で参照する。**ページ固有の `<style>`
    ブロックを章ページに個別で持たせない**（過去にそうしていたため、目次ページとフォントが
    不一致になるバグがあった。詳細は下記「デザイン・スタイルの規約」）。
  - `docs/citation-links.js` — 本文中の引用番号 `(55)` 等を実行時に `13_references.html#ref-55`
    へのリンクに変換するクライアントサイドJS。詳細は後述。
  - `docs/images/` — 図版画像（`scripts/extract_figures.py` の出力先）
  - `docs/<chunk_id>.html` — 各章ページ（`scripts/generate_docs.py` の出力）

## HTML生成パイプライン

典型的な1チャンクぶんの作業フローは次の通り：

1. `source/<chunk_id>.txt` を読み、`translations/ja/<chunk_id>.md` に翻訳を書く
   （記法は後述「Markdown記法の規約」に従う）。図版がある場合は、先に
   `scripts/extract_figures.py` で該当ページから画像を `docs/images/` へ切り出しておく
   （後述「図版の抽出」）。
2. `scripts/generate_docs.py` を実行し、`translations/ja/<chunk_id>.md` から
   `docs/<chunk_id>.html` を生成する（引数なしで全チャンク、またはチャンクIDを指定して
   個別に再生成できる：`python3 scripts/generate_docs.py 09c_technical_safeguards_monitoring`）。
   新しいチャンクを追加した場合は、このスクリプト冒頭の `CHAPTERS` リストに
   `(stem, "パンくず用タイトル")` を追加すること（リストに無いファイルは生成されない）。
3. `docs/index.html` の目次（`<ol class="toc-list">`）に該当行を追加・更新する。
   - リンク可能な項目: `<li><a href="xxx.html">日本語タイトル<span class="en">English title</span></a><span class="badge done">翻訳済み</span></li>`
   - 専用ページを持たない章の見出し（例: 「第1章 汎用AIの背景」のように、配下の節だけが
     それぞれ別ページを持つ場合）は `class="group"` を付け、リンクも `badge` も付けない：
     `<li class="group">第1章 汎用AIの背景 <span class="en">Background on general-purpose AI</span></li>`
     （`group` は本文とは別にスタイルされ、クリックできる項目と見分けがつくようになっている。
     詳細は `docs/style.css` の `.toc-list li.group`）。
   - サブ項目には `class="sub"` を付ける。
   - 未翻訳の章には `class="pending"` と `<span class="badge todo">未翻訳</span>` を付ける
     （`pending` は `pointer-events: none` でクリック不可になる）。
   - Usage Policy により一部未記載の節には `<span class="badge partial">一部未記載（Usage Policy）</span>`
     も追加する（上記「Anthropic Usage Policy に抵触する記載の扱い」参照）。
4. 参考文献番号を新規に翻訳した場合、`node scripts/build_references_html.js` を再実行して
   `docs/13_references.html` を最新化する必要は通常ない（参考文献リストは原文をまとめて
   一度に変換する想定）。ただし `source/13_references.txt` 自体を編集した場合は再実行すること。

## Markdown記法の規約（`translations/ja/*.md`）

`scripts/generate_docs.py` は以下の記法を前提にパースする。この規約から外れる書き方をすると、
正しくHTML化されない（過去に実際、この不一致が原因で "Table X.X:" のような見出しが本文に
埋め込まれて表示されるバグが起きた）。迷ったら既存の翻訳済みファイル（例:
`translations/ja/09a_technical_institutional_challenges.md`）を参考にする。

- ファイル先頭の `<!-- 原文: source/xxx.txt (PDF p.N-M) -->` のようなHTMLコメントは出典メモ。
  自動的に除去されるので、翻訳元ファイルの参照として全ファイルの先頭に書く。
- `# 見出し` が1つだけの場合、それがそのままページの `<h1>` になる。
  **2つある場合**（例: `08a1_ai_generated_content_crime.md` のように、節ファイルの冒頭に
  親章の見出し「`# 2.1. 悪意ある利用によるリスク`」と、続けてそのファイル自体の見出し
  「`# 2.1.1. AI生成コンテンツと犯罪活動`」の両方が書かれているケース）は、**最後の `#` 見出し**
  が `<h1>` になり、それより前の `#` 見出しはページ上部に小さな「`.chapter-kicker`」として
  表示される（親章の見出しを失わないための措置）。
- `## 見出し` → `<h2>`、`### 見出し` → `<h3>`。
- `- 項目` の連続 → `<ul>`。`1. 項目` のような数字始まりの連続 → `<ol>`。
- `**Table X.X: タイトル**` または `**Box X.X: タイトル**` のように、**1行がまるごと太字で
  `Table`/`Box` + 番号 + コロンから始まる場合**、これは表・ボックスの見出しとして
  `<p class="block-title"><strong>...</strong></p>` に変換される（通常の太字強調 `**text**`
  とは別扱い。行全体がこのパターンに一致しないと発動しないので、通常の文中強調と混同しない）。
- `*Table X.X: 全文キャプション...*`（1行まるごと単一アスタリスクで囲まれ、`Table`/`Box` +
  番号 + コロンから始まる）は、表の下に置くキャプションとして
  `<p class="caption"><em>...</em></p>` に変換される。
- Markdownパイプテーブル（`| ... |` の連続）→ `<table>`。1行目がヘッダ、2行目が `|---|---|`
  区切り、以降がデータ行。
- `![Figure X.X: 短い説明](path/to/fig_N_M.png)` → `<figure><img ...></figure>`。
  **パスのうち実際に使われるのはファイル名部分（`fig_` で始まる部分）だけ**なので、パスの
  プレフィックスが `../../docs/images/` だろうと多少古い表記だろうと実害はない。ただし
  ファイル名は `docs/images/` に実在するものと一致させること。
  この行の直後（空行を挟んで）に `> Figure X.X: 全文キャプション...` という blockquote が
  続く場合、それを図の正式なキャプションとして `<figcaption>` に使う（無ければ `![...]` の
  短い説明がそのまま `<figcaption>` になる）。
- `> 引用文` （上記の図キャプション以外の単独の blockquote）→ `<blockquote>`。
- 脚注: 本文中に脚注記号 `†` を書き、どこか別の段落に `† 脚注本文...` という行を置けば、
  自動的に `<sup id="fnref-N"><a href="#fn-N">†</a></sup>` と、ページ末の
  `<div class="footnotes">` 内の対応するリンク付き脚注項目に変換される（`N` は自動採番）。
  既に `<sup id="fnref-X"><a href="#fn-X">†</a></sup>` の形で手書きしてある場合はそのIDを
  尊重する。箇条書き項目の中の脚注記号にも対応している。
- フェンスコードブロック（` ``` ... ``` `）→ `<pre><code>`（HTMLエスケープ済み）。BibTeX等。
- `<div class="任意のクラス">...</div>` のような生HTMLブロックは、開始タグ・終了タグを
  単独の行として書けばそのままパススルーされる（中の段落は通常のMarkdownとして処理される）。
  Usage Policy注記（`.aup-note`）で使用。
- `---` だけの行 → `<hr>`。
- 引用番号 `(55)`, `(1149*)`, `(1228-1232)` 等は**特別な記法を使わず、ただの文章として
  括弧書きする**。太字・イタリックにしたり、Markdownリンクにしたりしない
  （`docs/citation-links.js` が表示時に自動でリンク化するため。詳細は次節）。
  ただし、引用番号中の `*`（例: `64*`）は単一アスタリスクのイタリック記法と衝突しうるため、
  `generate_docs.py` 側で「数字の直後の `*`」を一時的に退避してからイタリック変換する処理を
  入れてある。通常の文章を書く分には意識する必要はないが、Pythonで後処理スクリプトを書く際は
  この挙動（`apply_footnote_markers` の前段にある `\d\*` の保護）を壊さないよう注意。
- 段落内で改行だけして引き続き同じ意味のまとまりを書きたい場合（例: Forewords の署名ブロック、
  How to cite this report の著者一覧）は、空行を挟まずに複数行を続けて書けばよい。
  `<br>` で連結された1つの `<p>` になる。

## デザイン・スタイルの規約

- 全ページ共通で `docs/style.css` を使う。章ページ個別の `<style>` ブロックは作らない
  （過去に章ページだけ独自フォント `'Segoe UI', Tahoma, ...` を指定していたため、目次ページ
  （`Hiragino Sans`, `Noto Sans JP` 等）とフォントが不一致になるバグがあった）。
- 日本語フォントスタックは `"Hiragino Sans", "Noto Sans JP", "Helvetica Neue", Arial, sans-serif`
  （`docs/style.css` の `body { font-family: ... }`）。**`Yu Gothic` は含めない**
  （Windowsでの表示が細すぎるとのフィードバックがあり除去済み。Windowsでは Noto Sans JP が
  入っていればそれを、無ければブラウザ標準フォントにフォールバックする）。
- 本文は `text-align: justify`（両端揃え）。長い未改行トークン（URL・メールアドレス等）が
  含まれる段落で、両端揃えが特定の行を異常に間延びさせる不具合があったため、
  `p, li { overflow-wrap: anywhere; }` を設定して長いトークンを折り返せるようにしてある。
  これらのプロパティは削除しないこと。
- ダークモード対応は `@media (prefers-color-scheme: dark)` と CSS変数（`--fg`, `--bg`,
  `--accent` 等）で行っている。新しい色を使う場合もこの変数を使うか、ダークモード版の値を
  対で追加すること。

## 参考文献リンクの仕組み

本文中の `(55)` や `(1149*)` のような引用番号は、ビルド時（Markdown→HTML変換時）には
リンクにせず、ただの文字列として出力する。かわりに `docs/citation-links.js` が各HTMLページの
`<script src="citation-links.js"></script>`（`generate_docs.py` が全章ページに自動付与）
によって読み込まれ、ページ表示時にDOMを走査して「丸括弧の中身が引用番号のパターン（数字、
任意で末尾に`*`、カンマ区切り、ハイフンによる範囲指定）とだけ一致する」括弧を見つけ、各数字を
`13_references.html#ref-<N>` へのリンクに書き換える。`A`, `SCRIPT`, `STYLE`, `CODE`, `PRE`
要素の中身は対象外。

この方式を取っている理由は、翻訳Markdownを書く際に引用番号を意識せずそのまま書けるようにする
ため（Markdownリンク記法で都度リンクを書く必要がない）。次年度版でこの仕組みを変更する
必要性は薄いが、もし引用番号の記法自体（例: 上付き文字化する等）を変える場合は
`docs/citation-links.js` の正規表現も合わせて更新すること。

## 図版の抽出

原文PDFの図（グラフ・チャート）の大半はベクター描画であり、PyMuPDFの埋め込み画像抽出
（`page.get_images()`）だけでは取得できない。`scripts/extract_figures.py` は、該当ページの
「Figure X.Y:」というキャプション文字列をPDF内で検索して位置を特定し、そのキャプションより
上にあるベクター描画・埋め込み画像すべての外接矩形を合算してその領域を3倍ズームで画像として
書き出す（ベクター図・埋め込み写真どちらにも同じロジックで対応できる）。

使い方:

```
python3 scripts/extract_figures.py <PDFページ番号>:<図番号>:<出力ファイル名(拡張子なし)> [...]
```

例:

```
python3 scripts/extract_figures.py 19:1.1:fig_1_1 20:1.2:fig_1_2
```

`<PDFページ番号>` は `source/*.txt` の `[[page N]]` マーカーに現れる、PDF自体が印字している
ページ番号（0始まりの内部インデックスではない）。`<図番号>` は原文中の "Figure X.Y:" の
"X.Y" 部分（"Figure " は含めない）。出力は `docs/images/<出力ファイル名>.png`。

どのページに目的の図があるか分からない場合は、該当 `source/*.txt` チャンクの中で
`Figure X.Y:` を検索すればよい（チャンクのヘッダーにPDFページ範囲が書いてある）。

**依存パッケージ**: `pymupdf`（`import fitz` は非推奨エイリアスなので `import pymupdf as fitz`
を使うこと。スクリプトは既にそうなっている）。このコンテナでは `python3`（3.11系）に
インストールされておらず、`python3.13` にのみ入っている場合があった。
`python3 -c "import pymupdf"` が失敗したら、`python3.13 -c "import pymupdf"` を試すか、
`pip install pymupdf`（必要に応じて `--break-system-packages`）でインストールすること。

## チャンク構成（`source/_manifest.md` より抜粋・翻訳単位）

翻訳の単位は「Top-level」列が "yes" のトップレベル章。トップレベル章の内側にあるサブセクション
ファイル（例: `07a_what_is_general_purpose_ai.txt` 等）は、長い章を分担・並行作業する際の
補助的な分割として用意している。実際の翻訳作業は、章が長い場合はサブセクション単位
（`07a`, `07b`, `07c`, `08a1`, `08a2`, ... のように）で行い、`translations/ja/` にも
そのサブセクション単位でファイルを作成している。

主なトップレベル章と対応する `translations/ja/` ファイル（2026年版での実績）:

1. `00_contributors.txt` → `00_contributors.md` — Contributors。人名・組織名・所属機関名は
   原文のまま、見出しラベルと説明文のみ翻訳。原文p.5の「Contents」（PDF自身の目次）は
   `01_acknowledgements.txt` の抽出テキスト後半に同梱されているが、本サイト自身の
   `docs/index.html` と重複するため翻訳対象から除外する。
2. `01_acknowledgements.txt` → `01_acknowledgements.md` — Acknowledgements。人名・組織名は
   原文のまま、見出しラベルと説明文のみ翻訳。
3. `02_forewords.txt` → `02_forewords.md` — Forewords（p.8に "Al"→"AI" 誤変換の既知不具合あり。
   上記「原文PDFの既知の抽出上の不具合」参照）。
4. `03_about_this_report.txt` → `03_about_this_report.md` — About this Report
5. `04_key_developments.txt` → `04_key_developments.md` — Key developments since the 2025 Report
6. `05_executive_summary.txt` → `05_executive_summary.md` — Executive summary
7. `06_introduction.txt` → `06_introduction.md` — Introduction
8. `07_background.txt` — Background on general-purpose AI。サブセクション単位で翻訳：
   `07a_what_is_general_purpose_ai.md`, `07b_current_capabilities.md`,
   `07c_capabilities_by_2030.md`
9. `08_risks.txt` — Risks。サブセクション単位で翻訳：
   `08a1_ai_generated_content_crime.md`, `08a2_influence_manipulation.md`,
   `08a3_cyberattacks.md`, `08a4_bio_chem_risks.md`, `08b1_reliability_challenges.md`,
   `08b2_loss_of_control.md`, `08c1_labour_market.md`, `08c2_human_autonomy.md`
10. `09_risk_management.txt` — Risk management。サブセクション単位で翻訳：
    `09a_technical_institutional_challenges.md`, `09b_risk_management_practices.md`,
    `09c_technical_safeguards_monitoring.md`（§3.3 Table 3.8 に Usage Policy 関連の
    部分的省略あり。上記「Anthropic Usage Policy に抵触する記載の扱い」参照）,
    `09d_open_weight_models.md`, `09e_building_societal_resilience.md`
11. `10_conclusion.txt` → `10_conclusion.md` — Conclusion
12. `11_glossary.txt` — Glossary（原文英語のまま。訳語の対応は `glossary.md` を参照。
    このファイル自体はHTML化していない）
13. `12_how_to_cite.txt` → `12_how_to_cite.md` — How to cite this report。見出し・説明文は
    翻訳するが、著者一覧とBibTeXエントリは書誌データそのものなので原文のまま
    （フェンスコードブロックで囲んで `<pre><code>` にする）。
14. `13_references.txt` — References。`translations/ja/` に中間Markdownは作らず、
    `scripts/build_references_html.js` が `source/13_references.txt` から直接
    `docs/13_references.html` を生成する。
15. `14_colophon.txt` → `14_colophon.md` — 奥付（発行者情報。全文翻訳）

**「Extended Summary」の定義**: このプロジェクトでは `04_key_developments.txt` +
`05_executive_summary.txt` + `06_introduction.txt` の3ファイルをまとめて
「Executive Summary + Extended Summary」の第一弾翻訳対象として扱った。

## 進め方（次年度版で一から作業する場合のチェックリスト）

1. 新しい原文PDFに差し替え、`python3 scripts/extract_chunks.py` を実行して `source/` を
   再生成する。ページ構成・章番号が変わっていないか `source/_manifest.md` を確認し、
   必要なら本ファイルの章リストも更新する。
2. `source/11_glossary.txt` の用語集に変更がないか確認し、あれば
   `scripts/glossary_translations.py` / `scripts/glossary_supplementary.py` を更新した上で
   `python3 scripts/build_glossary.py` を再実行して `glossary.md` を更新する。
3. Key developments / Executive summary / Introduction を翻訳し、`translations/ja/` に保存する。
4. 以降、章単位（長い章はサブセクション単位）で翻訳を進める。各ファイルを書いたら
   随時 `python3 scripts/generate_docs.py <chunk_id>` でHTML化して見た目を確認する
   （特に表・図・脚注・Usage Policy注記まわりは、生成後に実際のHTMLを読んで
   崩れていないか確認すること。過去に発生した不具合は上記「Markdown記法の規約」を参照）。
5. 図版が出てきたら `scripts/extract_figures.py` でその都度切り出す。
6. 各章の翻訳が完了次第、`docs/index.html` の目次を更新する（リンク・バッジ・`group`/`sub`
   クラスの付け方は上記「HTML生成パイプライン」を参照）。
7. `source/13_references.txt` に変更があれば `node scripts/build_references_html.js` を
   再実行する（参考文献1451件という件数チェックがあるので、件数が変わっていたらスクリプト
   冒頭の期待値も更新すること）。
8. 全体を通して、翻訳ルール（である調、省略禁止、脚注・引用番号維持、人名・組織名は原文のまま、
   専門用語は初出時英語併記）を遵守できているか見直す。
