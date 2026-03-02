(() => {
  const root = document.getElementById('round1SummaryPage');
  if (!root) return;

  const saveUrl = root.dataset.saveUrl;
  const round = Number(root.dataset.round || 1);
  let startedAt = Date.now();
  let persisted = false;
  let inFlight = null;

  const continueButtons = Array.from(document.querySelectorAll('.continue-link-button'));

  const elapsedSeconds = () => Math.max(0, (Date.now() - startedAt) / 1000);

  const saveDuration = ({ bestEffort = false } = {}) => {
    if (persisted || inFlight) return inFlight || Promise.resolve();

    const payload = {
      round,
      duration_seconds: elapsedSeconds(),
    };

    if (bestEffort && navigator.sendBeacon) {
      const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
      persisted = navigator.sendBeacon(saveUrl, blob);
      return Promise.resolve();
    }

    inFlight = fetch(saveUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive: true,
    }).then((response) => {
      if (response?.ok) persisted = true;
    }).catch(() => {
      // ignore network errors
    }).finally(() => {
      inFlight = null;
    });

    return inFlight;
  };

  continueButtons.forEach((button) => {
    button.addEventListener('click', () => {
      saveDuration({ bestEffort: true });
    });
  });

  window.addEventListener('beforeunload', () => {
    saveDuration({ bestEffort: true });
  });
})();
