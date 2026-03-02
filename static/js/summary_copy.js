(() => {
  const copyBtn = document.getElementById('copyParticipantBtn');
  const codeNode = document.getElementById('participantCode');
  const statusNode = document.getElementById('copyStatus');

  if (!copyBtn || !codeNode) return;

  const setStatus = (text) => {
    if (!statusNode) return;
    statusNode.textContent = text;
    setTimeout(() => {
      if (statusNode.textContent === text) statusNode.textContent = '';
    }, 2000);
  };

  const selectCodeText = () => {
    const selection = window.getSelection();
    if (!selection) return;
    const range = document.createRange();
    range.selectNodeContents(codeNode);
    selection.removeAllRanges();
    selection.addRange(range);
  };

  const fallbackCopy = (text) => {
    const temp = document.createElement('textarea');
    temp.value = text;
    temp.setAttribute('readonly', '');
    temp.style.position = 'fixed';
    temp.style.left = '-9999px';
    document.body.appendChild(temp);
    temp.select();

    let ok = false;
    try {
      ok = document.execCommand('copy');
    } catch {
      ok = false;
    }

    document.body.removeChild(temp);
    return ok;
  };

  copyBtn.addEventListener('click', async () => {
    const code = (codeNode.textContent || '').trim();
    if (!code) return;

    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(code);
        setStatus('已复制');
        return;
      }

      if (fallbackCopy(code)) {
        setStatus('已复制');
        return;
      }

      selectCodeText();
      setStatus('复制失败，请手动复制');
    } catch {
      if (fallbackCopy(code)) {
        setStatus('已复制');
        return;
      }

      selectCodeText();
      setStatus('复制失败，请手动复制');
    }
  });
})();
