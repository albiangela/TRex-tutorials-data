const tabs = [...document.querySelectorAll('[role="tab"]')];
const panels = [...document.querySelectorAll('[role="tabpanel"]')];
function selectTab(id, focus = false) {
  const selected = tabs.find(tab => tab.getAttribute('aria-controls') === id) || tabs[0];
  tabs.forEach(tab => {
    const active = tab === selected;
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
  });
  panels.forEach(panel => { panel.hidden = panel.id !== selected.getAttribute('aria-controls'); });
  if (focus) selected.focus();
}
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => {
    const id = tab.getAttribute('aria-controls');
    history.pushState(null, '', '#' + id);
    selectTab(id);
  });
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next !== undefined) {
      event.preventDefault();
      tabs[next].click();
      tabs[next].focus();
    }
  });
});
window.addEventListener('hashchange', () => selectTab(location.hash.slice(1)));
window.addEventListener('popstate', () => selectTab(location.hash.slice(1)));
selectTab(location.hash.slice(1));
