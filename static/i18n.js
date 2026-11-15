/* Bundled interface localization. Never scans or translates user content. */
(() => {
  'use strict';
  const locales = ['en', 'de', 'es', 'ja', 'zh-CN', 'zh-TW'];
  const names = ['English', 'Deutsch', 'Español', '日本語', '简体中文', '繁體中文'];
  const catalog = globalThis.APP_MESSAGES || {};
  const storageKey = 'interface-language-v1';
  const bindings = new Map();
  function resolve(preferences) {
    for (const raw of preferences || []) {
      const tag = String(raw).toLowerCase().replaceAll('_', '-');
      if (/^zh(?:-|$)/.test(tag)) return /(?:^|-)(tw|hk|mo|hant)(?:-|$)/.test(tag) ? 'zh-TW' : 'zh-CN';
      const base = tag.split('-')[0];
      if (locales.includes(base)) return base;
    }
    return 'en';
  }
  let saved; try { saved = localStorage.getItem(storageKey); } catch {}
  let locale = locales.includes(saved) ? saved : resolve(navigator.languages || [navigator.language]);
  function t(source, values = {}) {
    const message = locale === 'en' ? source : (catalog[source]?.[locale] || source);
    return message.replace(/\{(\d+)\}/g, (match, key) => Object.hasOwn(values, key) ? String(values[key]) : match);
  }
  function text(node, source, values = {}) {
    if (!node) return;
    const leaf = document.createTextNode(t(source, values));
    node.replaceChildren(leaf);
    bindings.set(leaf, {source, values});
    queueMicrotask(() => { for (const item of bindings.keys()) if (!item.isConnected) bindings.delete(item); });
  }
  function paint() {
    document.documentElement.lang = locale;
    for (const input of document.querySelectorAll('[data-interface-locale]')) input.value = locale;
    for (const node of document.querySelectorAll('[data-i18n]')) node.textContent = t(node.dataset.i18n);
    for (const attribute of ['placeholder','aria-label','title']) {
      for (const node of document.querySelectorAll(`[data-i18n-${attribute}]`)) node.setAttribute(attribute, t(node.getAttribute(`data-i18n-${attribute}`)));
    }
    for (const [node, binding] of bindings) {
      if (!node.isConnected) { bindings.delete(node); continue; }
      node.textContent = t(binding.source, binding.values);
    }
    for (const select of document.querySelectorAll('[data-language-picker]')) select.value = locale;
  }
  function setLocale(value) {
    if (!locales.includes(value)) return;
    locale = value;
    try { localStorage.setItem(storageKey, value); } catch {}
    paint();
    window.dispatchEvent(new CustomEvent('languagechange-local', {detail: {locale}}));
  }
  function init() {
    const host = document.querySelector('[data-language-host]') || document.querySelector('header') || document.querySelector('main') || document.body;
    const label = document.createElement('label'); label.className = 'language-picker';
    const caption = document.createElement('span'); caption.dataset.i18n = 'Language'; caption.textContent = 'Language';
    const select = document.createElement('select'); select.dataset.languagePicker = '';
    locales.forEach((value, i) => { const option = new Option(names[i], value); option.lang = value; select.add(option); });
    select.addEventListener('change', () => setLocale(select.value)); label.append(caption, select); host.prepend(label);
    paint();
  }
  function option(source, value) { const node = new Option('',value); text(node,source); return node; }
  globalThis.I18n = {t, text, option, resolve, setLocale, get locale() {return locale;}, locales};
  window.addEventListener('storage', e => { if(e.key === storageKey && locales.includes(e.newValue)) {locale=e.newValue;paint();} });
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once:true}); else init();
})();
