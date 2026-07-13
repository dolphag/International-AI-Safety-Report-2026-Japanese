#!/usr/bin/env node

/**
 * Converts the figure placeholders in translations/ja/*.md to embedded images.
 * Markdown files are two directories below the repository root, hence the
 * ../../html/images/ path.
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
    return `![${figure}: ${caption}${note}](../../html/images/${image})`;
  });

  if (replacements > 0) {
    fs.writeFileSync(file, output, 'utf8');
    changedFiles += 1;
    embeddedFigures += replacements;
  }
}

console.log(`Embedded ${embeddedFigures} figure(s) in ${changedFiles} Markdown file(s).`);
