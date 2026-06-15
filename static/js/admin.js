(function () {
  "use strict";

  function bindAdminMenu() {
    App.qsa("[data-admin-target]").forEach(function (button) {
      App.on(button, "click", function () {
        var targetId = button.dataset.adminTarget;

        App.qsa("[data-admin-target]").forEach(function (item) {
          item.classList.toggle("active", item === button);
        });

        App.qsa("[data-admin-panel]").forEach(function (panel) {
          panel.hidden = panel.id !== targetId;
        });
      });
    });
  }

  function bindSearch() {
    App.qsa("[data-admin-search]").forEach(function (input) {
      var targetId = input.dataset.adminSearch;
      var target = document.getElementById(targetId);

      if (!target) {
        return;
      }

      App.on(input, "input", function () {
        var query = input.value.trim().toLowerCase();

        App.qsa("[data-search-row]", target).forEach(function (row) {
          row.hidden = query && !row.textContent.toLowerCase().includes(query);
        });
      });
    });
  }

  function bindUploadZones() {
    App.qsa("[data-upload-zone]").forEach(function (zone) {
      var input = zone.querySelector("input[type='file']");
      var label = zone.querySelector("[data-upload-label]");

      ["dragenter", "dragover"].forEach(function (eventName) {
        App.on(zone, eventName, function (event) {
          event.preventDefault();
          zone.classList.add("is-dragover");
        });
      });

      ["dragleave", "drop"].forEach(function (eventName) {
        App.on(zone, eventName, function (event) {
          event.preventDefault();
          zone.classList.remove("is-dragover");
        });
      });

      App.on(zone, "drop", function (event) {
        if (!input || !event.dataTransfer.files.length) {
          return;
        }

        input.files = event.dataTransfer.files;
        updateUploadLabel(input, label);
      });

      App.on(input, "change", function () {
        updateUploadLabel(input, label);
      });
    });
  }

  function updateUploadLabel(input, label) {
    if (!label || !input.files.length) {
      return;
    }

    label.textContent = input.files.length === 1 ? input.files[0].name : input.files.length + " files selected";
  }

  function bindAdminForms() {
    App.qsa("[data-admin-form]").forEach(function (form) {
      App.on(form, "submit", async function (event) {
        event.preventDefault();

        var submit = form.querySelector("[type='submit']");
        var endpoint = form.dataset.endpoint;
        var formData = new FormData(form);
        var hasFiles = Boolean(form.querySelector("input[type='file']"));
        var body = hasFiles ? formData : JSON.stringify(Object.fromEntries(formData.entries()));
        var headers = hasFiles ? {} : { "Content-Type": "application/json" };

        if (!endpoint) {
          App.showAlert("Missing form endpoint.", "danger");
          return;
        }

        App.setButtonLoading(submit, true, "Saving...");

        try {
          await App.apiFetch(endpoint, {
            method: form.dataset.method || "POST",
            headers: headers,
            body: body
          });
          App.showAlert("Saved successfully.", "success");
          form.reset();
        } catch (error) {
          App.showAlert(error.message, "danger");
        } finally {
          App.setButtonLoading(submit, false);
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindAdminMenu();
    bindSearch();
    bindUploadZones();
    bindAdminForms();
  });
})();
