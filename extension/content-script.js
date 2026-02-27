const MAX_TEXT_LENGTH = 1_000;

function parseTextContent(maxLen) {
  if (!document.body?.innerText) {
    return "";
  }
  content = document.body.innerText.trim().slice(0, maxLen);
  headers = document.querySelectorAll("h1, h2, h3, h4")
  return Array.from(headers).map(element => 
    {
      const clone = element.cloneNode(true)
      clone.removeAttribute("class")
      clone.removeAttribute("style")
      return clone.outerHTML
    }).join(' ') + "   " + content
}

window.addEventListener('load', (event) => {
  const payload = {
    type: "view",
    url: location.href,
    title: document.title || "",
    lang: document.documentElement?.lang || "",
    text: parseTextContent(MAX_TEXT_LENGTH)
  };

  chrome.runtime.sendMessage(payload);
});