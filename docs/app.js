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

const demoResponses = {
  ask: {
    title: "Preview Response",
    result:
      "This is a static preview. Run the backend to get real biotech answers.",
    details:
      "Tip: start the server with `python app.py`, then open http://localhost:8000.",
  },
  task: {
    title: "Preview Task",
    result: "Sequence tasks require the backend to compute real results.",
    details: "Once running, you can calculate GC content, reverse complement, and translate.",
  },
};

askButton.addEventListener("click", () => {
  const message = questionEl.value.trim();
  if (!message) {
    renderResponse({ error: "Please type a question first." });
    return;
  }
  renderResponse(demoResponses.ask);
});

runTaskButton.addEventListener("click", () => {
  const sequence = sequenceInput.value.trim();
  if (!sequence) {
    renderResponse({ error: "Please provide a sequence." });
    return;
  }
  renderResponse(demoResponses.task);
});
