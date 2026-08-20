window.mrAyo = {
  send: (message) => window.dispatchEvent(new CustomEvent('mr-ayo-send', { detail: message }))
};
