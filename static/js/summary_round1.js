(() => {
  const root = document.getElementById('round1SummaryPage');
  if (!root) return;

  const saveUrl = root.dataset.saveUrl;
  const round = Number(root.dataset.round || 1);
  const minViewSeconds = 30;
  let startedAt = Date.now();
  let persisted = false;
  let inFlight = null;
  let gateTimer = null;

  const continueButtons = Array.from(document.querySelectorAll('.continue-link-button'));
  const countdownHint = document.createElement('p');
  countdownHint.id = 'summaryCountdownHint';
  countdownHint.setAttribute('aria-live', 'polite');
  countdownHint.style.marginTop = '10px';

  const nextStepContent = root.querySelector('.next-step-content');
  if (nextStepContent) {
    nextStepContent.appendChild(countdownHint);
  }

  const elapsedSeconds = () => Math.max(0, (Date.now() - startedAt) / 1000);
  const remainingSeconds = () => Math.max(0, minViewSeconds - elapsedSeconds());

  const setContinueButtonsEnabled = (enabled) => {
    continueButtons.forEach((button) => {
      button.style.pointerEvents = enabled ? 'auto' : 'none';
      button.style.opacity = enabled ? '1' : '0.6';
      button.setAttribute('aria-disabled', enabled ? 'false' : 'true');
      button.setAttribute('tabindex', enabled ? '0' : '-1');
    });
  };

  const updateGateState = () => {
    const remaining = Math.ceil(remainingSeconds());
    if (remaining <= 0) {
      setContinueButtonsEnabled(true);
      if (countdownHint) {
        countdownHint.textContent = '已满30秒，现在可以点击“继续”。';
      }
      if (gateTimer) {
        clearInterval(gateTimer);
        gateTimer = null;
      }
      return;
    }

    setContinueButtonsEnabled(false);
    if (countdownHint) {
      countdownHint.textContent = `请至少停留 ${remaining} 秒后继续。`;
    }
  };

  updateGateState();
  gateTimer = window.setInterval(updateGateState, 500);

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
    button.addEventListener('click', (event) => {
      if (remainingSeconds() > 0) {
        event.preventDefault();
        return;
      }
      saveDuration({ bestEffort: true });
    });
  });

  window.addEventListener('beforeunload', () => {
    saveDuration({ bestEffort: true });
  });
})();
