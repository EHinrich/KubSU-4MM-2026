const IGNORE_URL_PREFIXES = [
  "chrome://"
];

function buildPayload(message) {
  return {
    url: message.url,
    title: message.title,
    lang: message.lang,
    text: message.text,
    timestamp: new Date().toISOString()
  };
}

chrome.runtime.onMessage.addListener(async (message) => {
  console.log("Received message", message);

  if (!message || message.type !== "view") {
    return; // Пустое или неподходящее сообщение
  }
  if (!message.url || IGNORE_URL_PREFIXES.some((prefix) => message.url.startsWith(prefix))) {
    return; // Пустой или неподходящий URL
  }

  const payload = buildPayload(message);
  console.log("Sending payload", payload); // TODO Send to Backend API
});