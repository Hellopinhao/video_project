(() => {
  const MAX_SELECTIONS = 3;
  const sliders = Array.from(document.querySelectorAll('.category-slider'));
  const form = document.getElementById('categoryForm');
  if (!sliders.length) return;

  const getValueNode = (slider) => slider.closest('.category-slider-item')?.querySelector('.category-value');
  const selectedCount = () => sliders.filter((slider) => Number(slider.value) > 0).length;
  const hasDuplicatePreference = () => {
    const values = sliders
      .map((slider) => Number(slider.value))
      .filter((value) => value > 0);
    return new Set(values).size !== values.length;
  };

  const refreshLocks = () => {
    const count = selectedCount();
    sliders.forEach((slider) => {
      const shouldDisable = count >= MAX_SELECTIONS && Number(slider.value) === 0;
      slider.disabled = shouldDisable;
    });
  };

  const syncSlider = (slider) => {
    const valueNode = getValueNode(slider);
    if (valueNode) valueNode.textContent = slider.value;
    slider.setAttribute('aria-valuenow', slider.value);
  };

  sliders.forEach((slider) => {
    slider.dataset.previousValue = slider.value;
    syncSlider(slider);
    slider.addEventListener('input', () => {
      slider.dataset.previousValue = slider.value;
      syncSlider(slider);
      refreshLocks();
    });
  });

  if (form) {
    form.addEventListener('submit', (event) => {
      if (selectedCount() !== MAX_SELECTIONS) {
        event.preventDefault();
        window.alert('请先选择3个偏好值大于0的视频类型。');
        return;
      }

      if (!hasDuplicatePreference()) return;
      event.preventDefault();
      window.alert('偏好值不能重复，请修改后再提交。');
    });
  }

  window.resetSliders = () => {
    sliders.forEach((slider) => {
      slider.value = '0';
      slider.dataset.previousValue = '0';
      slider.disabled = false;
      syncSlider(slider);
    });
  };

  refreshLocks();
})();
