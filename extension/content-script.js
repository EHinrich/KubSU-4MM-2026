const MAX_TEXT_LENGTH = 1_000;

function getBodyText(maxLen) {
  if (!document.body?.innerText) {
    return "";
  }
  return document.body.innerText.trim().slice(0, maxLen);
}

function getTextBySelectors(selectors) {
  const headers = [];
  document.querySelectorAll(selectors).forEach((header) => {
    headers.push(header.innerText.trim());
  });
  return headers.join(".");
}

window.addEventListener('load', (event) => {
  const payload = {
    type: "view",
    url: location.href,
    title: document.title || "",
    lang: document.documentElement?.lang || "",
    text: getBodyText(MAX_TEXT_LENGTH),
    headers: getTextBySelectors("h1")
  };

  chrome.runtime.sendMessage(payload);
});