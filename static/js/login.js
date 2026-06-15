(function () {
  "use strict";

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function setFieldError(field, message) {
    var wrapper = field.closest(".field") || field.parentElement;
    var error = wrapper ? wrapper.querySelector(".form-error") : null;

    field.setAttribute("aria-invalid", message ? "true" : "false");
    if (error) {
      error.textContent = message || "";
    }
  }

  function validateForm(form) {
    var valid = true;
    var email = form.querySelector("[name='email']");
    var password = form.querySelector("[name='password']");
    var confirmPassword = form.querySelector("[name='confirm_password']");

    if (email) {
      var emailValue = email.value.trim();
      var emailError = validateEmail(emailValue) ? "" : "Enter a valid email address.";
      setFieldError(email, emailError);
      valid = valid && !emailError;
    }

    if (password) {
      var passwordError = password.value.length >= 8 ? "" : "Password must be at least 8 characters.";
      setFieldError(password, passwordError);
      valid = valid && !passwordError;
    }

    if (confirmPassword) {
      var confirmError = confirmPassword.value === password.value ? "" : "Passwords do not match.";
      setFieldError(confirmPassword, confirmError);
      valid = valid && !confirmError;
    }

    return valid;
  }

  function bindPasswordToggles() {
    App.qsa("[data-toggle-password]").forEach(function (button) {
      App.on(button, "click", function () {
        var input = document.getElementById(button.dataset.togglePassword);
        if (!input) {
          return;
        }

        var showing = input.type === "text";
        input.type = showing ? "password" : "text";
        button.textContent = showing ? "Show" : "Hide";
        button.setAttribute("aria-pressed", showing ? "false" : "true");
      });
    });
  }

  function bindAuthForm() {
    var form = App.qs("[data-auth-form]");
    if (!form) {
      return;
    }

    App.on(form, "submit", async function (event) {
      event.preventDefault();

      if (!validateForm(form)) {
        App.showAlert("Please fix the highlighted fields.", "danger");
        return;
      }

      var submit = form.querySelector("[type='submit']");
      var endpoint = form.dataset.endpoint || "/auth/login";
      var redirect = form.dataset.redirect || "/dashboard";
      var remember = Boolean(form.querySelector("[name='remember']:checked"));
      var payload = Object.fromEntries(new FormData(form).entries());

      delete payload.remember;
      App.setButtonLoading(submit, true, "Signing in...");

      try {
        var result = await App.apiFetch(endpoint, {
          method: "POST",
          body: JSON.stringify(payload)
        });

        if (result.access_token) {
          App.setToken(result.access_token, remember);
        }

        window.location.href = redirect;
      } catch (error) {
        App.showAlert(error.message, "danger");
      } finally {
        App.setButtonLoading(submit, false);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindPasswordToggles();
    bindAuthForm();
  });
})();
