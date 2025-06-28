function switchFont(fontId) {
  document.querySelectorAll('.font-content').forEach(c => c.classList.remove('active'));
  const newContent = document.getElementById(fontId);
  newContent.classList.add('active');
  document.querySelectorAll('.tab-link').forEach(t => t.classList.remove('active'));
  document.querySelector(`[onclick="switchFont('${fontId}')"]`).classList.add('active');

  document.querySelectorAll('.nav a').forEach(n => n.classList.remove('active'));
  const firstNav = newContent.querySelector('.nav a');
  if (firstNav) firstNav.classList.add('active');

  newContent.querySelectorAll('section[id^="' + fontId + '_blk_"]').forEach(s => {
    showPage(fontId, s.id, 1);
  });
}

function showPage(fontId, blockId, pageNum) {
  const section = document.querySelector(`#${fontId} #${blockId}`);
  if (!section) return;
  section.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const target = section.querySelector('.page-' + pageNum);
  if (target) target.classList.add('active');
  section.querySelectorAll('.pagination button').forEach(b => b.classList.remove('active'));
  const btn = section.querySelector('.page-btn-' + pageNum);
  if (btn) btn.classList.add('active');
}

document.addEventListener('DOMContentLoaded', function() {
  function activateByHash() {
    const hash = window.location.hash;
    if (!hash) return false;
    const m = hash.slice(1).match(/^([^_]+_[^_]+)_blk_(.+)$/);
    if (!m) return false;
    const fontId = m[1];
    const blockId = `${fontId}_blk_${m[2]}`;

    const tabLink = document.querySelector(`[onclick="switchFont('${fontId}')"]`);
    if (!tabLink) return false;
    switchFont(fontId);

    const navLink = document.querySelector(`a[href="${hash}"]`);
    if (navLink) {
      const nav = navLink.closest('.nav');
      nav.querySelectorAll('a').forEach(a => a.classList.remove('active'));
      navLink.classList.add('active');
      const section = document.getElementById(blockId);
      if (section) section.scrollIntoView();
    }
    return true;
  }

  if (!activateByHash()) {
    const firstTab = document.querySelector('.tab-link');
    if (firstTab) firstTab.click();
  }

  function initResizer() {
    const containers = document.querySelectorAll('.container');
    containers.forEach(container => {
      const nav = container.querySelector('.nav');
      if (!nav) return;

      // 创建拖拽手柄
      const resizer = document.createElement('div');
      resizer.className = 'resizer';
      nav.insertAdjacentElement('afterend', resizer);

      let isResizing = false;
      let startX = 0;
      let startWidth = 0;
      let latestX = 0;
      let ticking = false;

      resizer.addEventListener('mousedown', function(e) {
        isResizing = true;
        startX = e.clientX;
        startWidth = nav.offsetWidth;
        nav.style.userSelect = 'none';
        document.body.style.cursor = 'col-resize';
        resizer.classList.add('dragging');
      });

      function onMouseMove(e) {
        if (!isResizing) return;
        latestX = e.clientX;
        if (!ticking) {
          window.requestAnimationFrame(updateWidth);
          ticking = true;
        }
      }

      function updateWidth() {
        const delta = latestX - startX;
        const newWidth = Math.min(
          Math.max(startWidth + delta, 150),
          window.innerWidth * 0.5
        );
        container.style.setProperty('--nav-width', newWidth + 'px');
        ticking = false;
      }

      function stopResizing() {
        if (!isResizing) return;
        isResizing = false;
        nav.style.userSelect = '';
        document.body.style.cursor = '';
        resizer.classList.remove('dragging');
      }

      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', stopResizing);
      // 为了兼容拖出 iframe / window 的情况，也可以监听 mouseleave
    });
  }

  initResizer();

  document.body.addEventListener('click', function(e) {
    const navLink = e.target.closest('.nav a');
    if (navLink) {
      const nav = navLink.closest('.nav');
      nav.querySelectorAll('a').forEach(n => n.classList.remove('active'));
      navLink.classList.add('active');
      return;
    }
    const item = e.target.closest('.glyph-item');
    if (!item) return;
    item
      .closest('.main')
      .querySelectorAll('.glyph-item.active')
      .forEach(el => el.classList.remove('active'));
    item.classList.add('active');
  });
});