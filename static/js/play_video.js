(() => {
  const root = document.getElementById('playerPage');
  const videoPlayer = document.getElementById('videoPlayer');
  if (!root || !videoPlayer) return;

  const cfg = {
    currentIndex: Number(root.dataset.currentIndex || 0),
    totalVideos: Number(root.dataset.totalVideos || 0),
    videoId: root.dataset.videoId || '',
    videoTitle: root.dataset.videoTitle || '',
    videoCategory: root.dataset.videoCategory || '',
    playBaseUrl: root.dataset.playBaseUrl || '/play_video/0',
    summaryUrl: root.dataset.summaryUrl || '/summary',
    saveWatchUrl: root.dataset.saveWatchUrl || '/save_watch_duration',
    likeUrl: root.dataset.likeUrl || '/like_video',
    commentUrl: root.dataset.commentUrl || '/add_comment',
    initialLikeStatus: root.dataset.likeStatus || '',
  };
  let currentLikeStatus = cfg.initialLikeStatus;
  let likeInFlight = false;
  let commentInFlight = false;

  let watchStartTime = Date.now();
  let totalWatchDuration = 0;
  let isPlaying = false;
  let saveInFlight = null;
  let hasPersisted = false;

  const navigateToIndex = (index) => {
    window.location.href = cfg.playBaseUrl.replace('/0', `/${index}`);
  };

  const likeBtn = document.querySelector('.like-button');
  const dislikeBtn = document.querySelector('.dislike-button');
  const feedbackStatus = document.getElementById('feedbackStatus');
  const commentInput = document.getElementById('commentInput');
  const commentStatus = document.getElementById('commentStatus');
  const commentLength = document.getElementById('commentLength');
  const sendButton = document.querySelector('.send-button');
  const sendButtonText = sendButton?.textContent || '发送';

  const updateCommentLength = () => {
    if (!commentInput || !commentLength) return;
    commentLength.textContent = `${commentInput.value.length} 字`;
  };

  updateCommentLength();

  const setStatus = (node, message, isError = false) => {
    if (!node) return;
    node.textContent = message;
    node.classList.toggle('error', Boolean(isError));
  };

  const setReactionButtonsDisabled = (disabled) => {
    likeBtn?.toggleAttribute('disabled', disabled);
    dislikeBtn?.toggleAttribute('disabled', disabled);
  };

  const applyReactionState = (status) => {
    likeBtn?.classList.toggle('active', status === 'like');
    dislikeBtn?.classList.toggle('active', status === 'dislike');
    likeBtn?.setAttribute('aria-pressed', status === 'like' ? 'true' : 'false');
    dislikeBtn?.setAttribute('aria-pressed', status === 'dislike' ? 'true' : 'false');
  };

  applyReactionState(currentLikeStatus);

  const stopWatchTimer = () => {
    if (isPlaying) {
      totalWatchDuration += (Date.now() - watchStartTime) / 1000;
      isPlaying = false;
    }
  };

  const getPayload = () => ({
    video_id: cfg.videoId,
    video_title: cfg.videoTitle,
    video_category: cfg.videoCategory,
    video_index: cfg.currentIndex,
    watch_duration: totalWatchDuration,
    video_total_duration: videoPlayer.duration || 0
  });

  const saveWatchDuration = ({ bestEffort = false } = {}) => {
    if (hasPersisted) return Promise.resolve();
    stopWatchTimer();
    const payload = JSON.stringify(getPayload());

    if (bestEffort && navigator.sendBeacon) {
      const blob = new Blob([payload], { type: 'application/json' });
      hasPersisted = navigator.sendBeacon(cfg.saveWatchUrl, blob);
      return Promise.resolve();
    }

    if (saveInFlight) return saveInFlight;

    saveInFlight = fetch(cfg.saveWatchUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: payload,
      keepalive: true
    }).then((response) => {
      if (response?.ok) {
        hasPersisted = true;
      }
    }).catch(() => {
      // Ignore network errors; caller decides navigation flow.
    }).finally(() => {
      saveInFlight = null;
    });

    return saveInFlight;
  };

  window.previousVideo = async () => {
    if (cfg.currentIndex <= 0) return;
    await saveWatchDuration();
    navigateToIndex(cfg.currentIndex - 1);
  };

  window.nextVideo = async ({ skipSave = false } = {}) => {
    if (!skipSave) {
      await saveWatchDuration();
    }
    if (cfg.currentIndex < cfg.totalVideos - 1) {
      navigateToIndex(cfg.currentIndex + 1);
      return;
    }
    window.location.href = cfg.summaryUrl;
  };

  window.goToSummary = () => {
    window.location.href = cfg.summaryUrl;
  };

  window.showSummaryButton = () => {
    const summaryContainer = document.getElementById('summaryButtonContainer');
    if (!summaryContainer) return;
    summaryContainer.classList.remove('hidden');
    summaryContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  window.likeVideo = (action) => {
    if (likeInFlight) return;
    likeInFlight = true;
    setReactionButtonsDisabled(true);
    setStatus(feedbackStatus, '正在保存反馈...');

    fetch(cfg.likeUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_id: cfg.videoId, action })
    })
      .then((response) => response.json())
      .then((data) => {
        if (!data.success) {
          setStatus(feedbackStatus, '反馈保存失败，请重试。', true);
          return;
        }

        const nextStatus = data.status || '';
        currentLikeStatus = nextStatus;
        applyReactionState(nextStatus);
        setStatus(
          feedbackStatus,
          nextStatus === 'like'
            ? '已标记为喜欢'
            : nextStatus === 'dislike'
              ? '已标记为不喜欢'
              : '已取消反馈'
        );
      })
      .catch(() => {
        setStatus(feedbackStatus, '网络异常，反馈未保存。', true);
      })
      .finally(() => {
        likeInFlight = false;
        setReactionButtonsDisabled(false);
      });
  };

  window.sendComment = () => {
    const commentText = commentInput?.value.trim();
    if (commentInFlight) return;

    if (!commentText) {
      setStatus(commentStatus, '请输入评论内容。', true);
      return;
    }

    commentInFlight = true;
    commentInput?.setAttribute('disabled', 'disabled');
    sendButton?.setAttribute('disabled', 'disabled');
    if (sendButton) sendButton.textContent = '发送中...';
    setStatus(commentStatus, '正在提交评论...');

    fetch(cfg.commentUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video_id: cfg.videoId, comment: commentText })
    })
      .then((response) => response.json())
      .then((data) => {
        if (!data.success) {
          setStatus(commentStatus, '评论提交失败，请重试。', true);
          return;
        }

        if (commentInput) commentInput.value = '';
        setStatus(commentStatus, '评论已记录。');
      })
      .catch(() => {
        setStatus(commentStatus, '网络异常，评论未保存。', true);
      })
      .finally(() => {
        commentInFlight = false;
        commentInput?.removeAttribute('disabled');
        sendButton?.removeAttribute('disabled');
        if (sendButton) sendButton.textContent = sendButtonText;
        updateCommentLength();
      });
  };

  commentInput?.addEventListener('input', () => {
    updateCommentLength();
  });

  commentInput?.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
      event.preventDefault();
      window.sendComment();
    }
  });

  videoPlayer.addEventListener('play', () => {
    watchStartTime = Date.now();
    isPlaying = true;
  });

  videoPlayer.addEventListener('playing', () => {
    if (isPlaying) return;
    watchStartTime = Date.now();
    isPlaying = true;
  });

  videoPlayer.addEventListener('pause', () => {
    stopWatchTimer();
  });

  videoPlayer.addEventListener('waiting', () => {
    stopWatchTimer();
  });

  videoPlayer.addEventListener('stalled', () => {
    stopWatchTimer();
  });

  videoPlayer.addEventListener('seeking', () => {
    stopWatchTimer();
  });

  videoPlayer.addEventListener('seeked', () => {
    if (videoPlayer.paused || videoPlayer.ended) return;
    watchStartTime = Date.now();
    isPlaying = true;
  });

  videoPlayer.addEventListener('ended', async () => {
    await saveWatchDuration();
    if (cfg.currentIndex >= cfg.totalVideos - 1) {
      setTimeout(window.showSummaryButton, 500);
      return;
    }
    setTimeout(() => window.nextVideo({ skipSave: true }), 1000);
  });

  window.addEventListener('beforeunload', () => {
    if (hasPersisted || saveInFlight) return;
    saveWatchDuration({ bestEffort: true });
  });

  setTimeout(() => {
    videoPlayer.play().catch(() => {});
  }, 500);
})();
