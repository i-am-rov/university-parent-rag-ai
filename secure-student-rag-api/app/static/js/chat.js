const chatForm = document.getElementById("chat-form");
const questionInput = document.getElementById("question");
const answerBox = document.getElementById("answer");
const sendButton = document.getElementById("send-button");

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = questionInput.value.trim();
  if (!question) {
    answerBox.textContent = "Please write a question first.";
    return;
  }

  answerBox.textContent = "Sending...";
  sendButton.disabled = true;

  try {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("Please login before asking a question.");
    }

    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ question })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const detail = Array.isArray(errorData.detail)
        ? errorData.detail.map((item) => item.msg).join(" ")
        : errorData.detail;
      throw new Error(detail || "Backend request failed.");
    }

    const data = await response.json();
    answerBox.textContent = data.answer;
  } catch (error) {
    answerBox.textContent = error.message;
  } finally {
    sendButton.disabled = false;
  }
});
