/* Reference-number links for the Japanese translation pages. */
(() => {
  'use strict';

  const referencePage = '13_references.html';
  const citationOnly = /^\s*\d{1,4}\*?(?:\s*[-–]\s*\d{1,4}\*?)?(?:\s*,\s*\d{1,4}\*?(?:\s*[-–]\s*\d{1,4}\*?)?)*\s*$/;
  const citationToken = /\d{1,4}\*?(?:\s*[-–]\s*\d{1,4}\*?)?/g;
  const excluded = new Set(['A', 'SCRIPT', 'STYLE', 'CODE', 'PRE']);

  function referenceId(token) {
    const match = token.match(/^\d+/);
    return match ? Number(match[0]) : 0;
  }

  function linkifyText(text) {
    return text.replace(/[（(]([^（）()]*)[）)]/g, (whole, contents) => {
      if (!citationOnly.test(contents)) return whole;

      const linked = contents.replace(citationToken, (token) => {
        const id = referenceId(token);
        if (id < 1 || id > 1451) return token;
        return `<a class="reference-citation" href="${referencePage}#ref-${id}" title="参考文献 ${token}">${token}</a>`;
      });
      return whole.startsWith('（') ? `（${linked}）` : `(${linked})`;
    });
  }

  function visit(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      if (!/[（(]/.test(node.nodeValue)) return;
      const holder = document.createElement('span');
      holder.innerHTML = linkifyText(node.nodeValue);
      if (holder.innerHTML !== node.nodeValue) node.replaceWith(...holder.childNodes);
      return;
    }
    if (node.nodeType !== Node.ELEMENT_NODE || excluded.has(node.tagName)) return;
    [...node.childNodes].forEach(visit);
  }

  document.addEventListener('DOMContentLoaded', () => visit(document.body));
})();
