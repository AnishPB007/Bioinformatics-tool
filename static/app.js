const responseEl = document.getElementById("response");
const questionEl = document.getElementById("question");
const askButton = document.getElementById("ask");
const taskSelect = document.getElementById("task");
const sequenceInput = document.getElementById("sequence");
const runTaskButton = document.getElementById("run-task");

const renderResponse = (payload) => {
  responseEl.innerHTML = "";

  if (payload.error) {
    responseEl.innerHTML = `<p class="error">${payload.error}</p>`;
    return;
  }

  const title = document.createElement("h3");
  title.textContent = payload.title || "Response";

  const result = document.createElement("p");
  result.textContent = payload.result || "";

  responseEl.appendChild(title);
  responseEl.appendChild(result);

  if (payload.details) {
    const details = document.createElement("p");
    details.className = "details";
    details.textContent = payload.details;
    responseEl.appendChild(details);
  }
};

const postJson = async (url, body) => {
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return await response.json();
  } catch (error) {
    return {
      error:
        "Cannot reach the backend. Start the server with `python app.py` and refresh.",
    };
  }
};

askButton.addEventListener("click", async () => {
  const message = questionEl.value.trim();
  if (!message) {
    renderResponse({ error: "Please type a question first." });
    return;
  }
  const payload = await postJson("/ask", { message });
  renderResponse(payload);
});

runTaskButton.addEventListener("click", async () => {
  const task = taskSelect.value;
  const sequence = sequenceInput.value.trim();
  if (!sequence) {
    renderResponse({ error: "Please provide a sequence." });
    return;
  }
  const payload = await postJson("/task", { task, sequence });
  renderResponse(payload);
});
