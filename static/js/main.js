(function () {
  "use strict";

  function qs(selector, scope) {
    return (scope || document).querySelector(selector);
  }

  function qsa(selector, scope) {
    return Array.prototype.slice.call((scope || document).querySelectorAll(selector));
  }

  function on(target, eventName, handler) {
    if (target) {
      target.addEventListener(eventName, handler);
    }
  }

  function getToken() {
    return localStorage.getItem("access_token") || sessionStorage.getItem("access_token") || "";
  }

  function setToken(token, remember) {
    var storage = remember ? localStorage : sessionStorage;
    storage.setItem("access_token", token);
  }

  function clearToken() {
    localStorage.removeItem("access_token");
    sessionStorage.removeItem("access_token");
  }

  async function apiFetch(url, options) {
    var request = options || {};
    var headers = Object.assign(
      { "Content-Type": "application/json", Accept: "application/json" },
      request.headers || {}
    );
    var token = getToken();

    if (token) {
      headers.Authorization = "Bearer " + token;
    }

    var response = await fetch(url, Object.assign({}, request, { headers: headers }));
    var contentType = response.headers.get("content-type") || "";
    var payload = contentType.includes("application/json") ? await response.json() : await response.text();

    if (!response.ok) {
      var message = payload && payload.detail ? payload.detail : "Request failed. Please try again.";
      throw new Error(message);
    }

    return payload;
  }

  function showAlert(message, type, container) {
    var target = container || qs("[data-alert-region]");
    if (!target) {
      return;
    }

    target.innerHTML = "";
    var alert = document.createElement("div");
    alert.className = "alert " + (type || "warning");
    alert.setAttribute("role", "status");
    alert.textContent = message;
    target.appendChild(alert);
  }

  function setButtonLoading(button, isLoading, label) {
    if (!button) {
      return;
    }

    if (isLoading) {
      button.dataset.originalText = button.textContent;
      button.textContent = label || "Working...";
      button.disabled = true;
    } else {
      button.textContent = button.dataset.originalText || button.textContent;
      button.disabled = false;
    }
  }

  function highlightCurrentNav() {
    var currentPath = window.location.pathname.replace(/\/$/, "") || "/";

    qsa(".nav a").forEach(function (link) {
      var linkPath = new URL(link.href, window.location.origin).pathname.replace(/\/$/, "") || "/";
      if (linkPath === currentPath) {
        link.setAttribute("aria-current", "page");
      }
    });
  }

  function bindLogout() {
    qsa("[data-logout]").forEach(function (button) {
      on(button, "click", function () {
        clearToken();
        window.location.href = button.dataset.redirect || "/login";
      });
    });
  }

  function bindDismissibleAlerts() {
    qsa("[data-dismiss-alert]").forEach(function (button) {
      on(button, "click", function () {
        var alert = button.closest(".alert");
        if (alert) {
          alert.remove();
        }
      });
    });
  }

  window.App = {
    qs: qs,
    qsa: qsa,
    on: on,
    apiFetch: apiFetch,
    getToken: getToken,
    setToken: setToken,
    clearToken: clearToken,
    showAlert: showAlert,
    setButtonLoading: setButtonLoading
  };

  document.addEventListener("DOMContentLoaded", function () {
    highlightCurrentNav();
    bindLogout();
    bindDismissibleAlerts();
  });
})();
