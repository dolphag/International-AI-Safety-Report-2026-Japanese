#!/usr/bin/env node

/**
 * Converts the figure placeholders in translations/ja/*.md to embedded images.
 * Markdown files are two directories below the repository root, hence the
 * ../../docs/images/ path. Only the filename (fig_N_M.png) is actually read
 * by scripts/generate_docs.py when building the HTML pages -- this path
 * prefix is cosmetic, so it can drift without breaking the site, but keep
 * it accurate for anyone reading the raw Markdown.
 */
const fs = require('fs');
const path = require('path');

const translationsDir = path.join(__dirname, '..', 'translations', 'ja');
const figurePattern = /^\*\*\[図: (Figure [^\]]+)\]\*\* — (.+?)（画像: `html\/images\/(fig_[^`]+)`([^）]*)）$/gm;

let changedFiles = 0;
let embeddedFigures = 0;

for (const name of fs.readdirSync(translationsDir).filter((file) => file.endsWith('.md'))) {
  const file = path.join(translationsDir, name);
  const input = fs.readFileSync(file, 'utf8');
  let replacements = 0;
  const output = input.replace(figurePattern, (_, figure, caption, image, note) => {
    replacements += 1;
    return `![${figure}: ${caption}${note}](../../docs/images/${image})`;
  });

  if (replacements > 0) {
    fs.writeFileSync(file, output, 'utf8');
    changedFiles += 1;
    embeddedFigures += replacements;
  }
}

console.log(`Embedded ${embeddedFigures} figure(s) in ${changedFiles} Markdown file(s).`);
