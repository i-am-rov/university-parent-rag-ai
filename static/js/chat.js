(function () {
  "use strict";

  function createMessage(role, text) {
    var message = document.createElement("article");
    message.className = "message " + role;

    var body = document.createElement("div");
    body.className = "message-body";
    body.textContent = text;

    var meta = document.createElement("div");
    meta.className = "message-meta";
    meta.textContent = role === "user" ? "You" : "University assistant";

    message.appendChild(body);
    message.appendChild(meta);
    return message;
  }

  function createTypingMessage() {
    var message = document.createElement("article");
    message.className = "message assistant";
    message.dataset.typing = "true";
    message.innerHTML = '<div class="typing-indicator" aria-label="Assistant is typing"><span></span><span></span><span></span></div>';
    return message;
  }

  function scrollToBottom(messages) {
    messages.scrollTop = messages.scrollHeight;
  }

  function bindPromptChips(input) {
    App.qsa("[data-prompt]").forEach(function (chip) {
      App.on(chip, "click", function () {
        input.value = chip.dataset.prompt || chip.textContent.trim();
        input.focus();
      });
    });
  }

  function bindChatForm() {
    var form = App.qs("[data-chat-form]");
    var input = App.qs("[data-chat-input]");
    var messages = App.qs("[data-chat-messages]");

    if (!form || !input || !messages) {
      return;
    }

    bindPromptChips(input);

    App.on(input, "keydown", function (event) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        form.requestSubmit();
      }
    });

    App.on(form, "submit", async function (event) {
      event.preventDefault();

      var question = input.value.trim();
      if (!question) {
        return;
      }

      var submit = form.querySelector("[type='submit']");
      var endpoint = form.dataset.endpoint || "/chat/ask";

      messages.appendChild(createMessage("user", question));
      input.value = "";
      var typing = createTypingMessage();
      messages.appendChild(typing);
      scrollToBottom(messages);
      App.setButtonLoading(submit, true, "Sending...");

      try {
        var result = await App.apiFetch(endpoint, {
          method: "POST",
          body: JSON.stringify({ question: question })
        });

        typing.remove();
        messages.appendChild(createMessage("assistant", result.answer || "I could not find an answer."));
      } catch (error) {
        typing.remove();
        messages.appendChild(createMessage("system", error.message));
      } finally {
        App.setButtonLoading(submit, false);
        scrollToBottom(messages);
        input.focus();
      }
    });
  }

  document.addEventListener("DOMContentLoaded", bindChatForm);
})();
