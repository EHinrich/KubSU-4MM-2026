const API_URL = "http://127.0.0.1:8000";

const queryInput = document.getElementById("queryInput");
const sendButton = document.getElementById("sendButton");
const historyButton = document.getElementById("historyButton");
const responseDiv = document.getElementById("response");

sendButton.addEventListener("click", () => sendRequest());
queryInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendRequest();
});

async function sendRequest() {
  const text = queryInput.value.trim();
  if (!text) return;

  sendButton.disabled = true;
  responseDiv.style.display = "block";
  responseDiv.textContent = "Загрузка...";

  try {
    const res = await fetch(`${API_URL}/request`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({"prompt": text}),
    });

    if (!res.ok) {
      throw new Error(`Ошибка: ${res.status} ${res.statusText}`);
    }

    const data = await res.json();
    responseDiv.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    responseDiv.textContent = `Ошибка: ${err.message}`;
  } finally {
    sendButton.disabled = false;
  }
}

historyButton.addEventListener("click", () => loadHistory());

async function loadHistory() {
  responseDiv.style.display = "block";
  responseDiv.textContent = "Загрузка...";

  try {
    const res = await fetch(`${API_URL}/history`);

    if (!res.ok) {
      throw new Error(`Ошибка: ${res.status} ${res.statusText}`);
    }

    const data = await res.json();
    responseDiv.innerHTML = `
        <h2>Сводка</h2>
        <p id="text"></p>

        <h3>Изображение</h3>
        <img id="img" style="max-width:512px; border-radius:10px;" />
    `;

    document.getElementById("text").textContent = data.text;

    document.getElementById("img").src = data.image;
  } catch (err) {
    responseDiv.textContent = `Ошибка: ${err.message}`;
  }
}