#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const htmlDir = path.join(root, 'html');
const source = fs.readFileSync(path.join(root, 'source', '13_references.txt'), 'utf8');
const entryStart = /^(\d+)(\*)?\s+(.+)$/;
const urlPattern = /https?:\/\/[^\s<]+/g;

function escapeHtml(value) {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function linkifyUrls(value) {
  return escapeHtml(value).replace(urlPattern, (url) => {
    const target = url.replace(/[.,;]+$/, '');
    const suffix = url.slice(target.length);
    return `<a href="${target}" target="_blank" rel="noopener noreferrer">${target}</a>${suffix}`;
  });
}

function parseEntries(text) {
  const entries = [];
  let current = null;
  let expected = 1;
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith('#') || line.startsWith('[[page ')) continue;
    if (line === 'References' || line === 'International AI Safety Report 2026' || /^\d+$/.test(line)) continue;
    const match = entryStart.exec(line);
    if (match && Number(match[1]) === expected) {
      if (current) entries.push(current);
      current = { number: expected, industry: Boolean(match[2]), parts: [match[3]] };
      expected += 1;
    } else if (current) {
      current.parts.push(line);
    }
  }
  if (current) entries.push(current);
  return entries.map((entry) => {
    const text = entry.parts.join(' ');
    const httpStart = Math.max(text.lastIndexOf('https://'), text.lastIndexOf('http://'));
    if (httpStart < 0) return entry;
    // PDF extraction can insert spaces inside a wrapped URL. Reference URLs
    // occur at the end of an entry, so their trailing substring is safe to join.
    entry.parts = [text.slice(0, httpStart) + text.slice(httpStart).replace(/\s+/g, '')];
    return entry;
  });
}

function buildReferences(entries) {
  const items = entries.map(({ number, industry, parts }) => {
    const star = industry ? '<span class="industry" title="企業関連文献">*</span>' : '';
    return `    <li id="ref-${number}"><span class="reference-number">${number}${star}</span> ${linkifyUrls(parts.join(' '))}</li>`;
  }).join('\n');
  return `<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>参考文献 — International AI Safety Report 2026 日本語訳</title>
<link rel="stylesheet" href="style.css">
<style>
  .references { list-style: none; padding: 0; }
  .references li { display: grid; grid-template-columns: 4.5rem minmax(0, 1fr); gap: .5rem; scroll-margin-top: 1.5rem; margin: .6em 0; overflow-wrap: anywhere; }
  .reference-number { min-width: 0; font-weight: 700; text-align: right; }
  .industry { color: #a13a00; }
  .reference-note { margin: 1.5em 0; padding: 1em; color: var(--fg); background: var(--accent-bg); border-left: 4px solid var(--accent); }
</style>
</head>
<body>
<div class="page">
  <div class="masthead">参考文献</div>
  <h1>参考文献</h1>
  <p>本文中の引用番号から参照できる書誌情報である。著者名、組織名、論文・資料の正式題名およびURLは、出典を正確に特定できるよう原文表記を維持している。</p>
  <div class="reference-note">番号末尾の <strong>*</strong> は、営利AI企業が公表した文献、または著者の過半数がそのような企業に所属する文献を表す。</div>
  <ol class="references">
${items}
  </ol>
  <p><a href="index.html">目次に戻る</a></p>
</div>
<footer class="site">原文: International AI Safety Report 2026（DSIT 2026/001, 2026年2月発行）。本サイトは非公式の日本語訳である。</footer>
</body>
</html>
`;
}

function attachCitationScript() {
  const tag = '<script src="citation-links.js"></script>';
  for (const name of fs.readdirSync(htmlDir)) {
    if (!name.endsWith('.html') || name === 'index.html' || name === '13_references.html') continue;
    const file = path.join(htmlDir, name);
    const text = fs.readFileSync(file, 'utf8');
    if (text.includes(tag)) continue;
    if (!text.includes('</body>')) throw new Error(`No closing body tag: ${name}`);
    fs.writeFileSync(file, text.replace('</body>', `${tag}\n</body>`), 'utf8');
  }
}

const entries = parseEntries(source);
if (entries.length !== 1451 || entries.at(-1).number !== 1451) {
  throw new Error(`Expected 1451 reference entries; found ${entries.length}`);
}
fs.writeFileSync(path.join(htmlDir, '13_references.html'), buildReferences(entries), 'utf8');
attachCitationScript();
console.log(`Wrote html/13_references.html with ${entries.length} entries`);
