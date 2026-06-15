(function () {
  "use strict";

  function animateNumber(element) {
    var target = Number(element.dataset.countTo || element.textContent.replace(/[^\d.]/g, ""));
    var prefix = element.dataset.prefix || "";
    var suffix = element.dataset.suffix || "";
    var duration = Number(element.dataset.duration || 700);
    var startTime = performance.now();

    if (!Number.isFinite(target)) {
      return;
    }

    function tick(now) {
      var progress = Math.min((now - startTime) / duration, 1);
      var value = target * progress;
      var display = Number.isInteger(target) ? Math.round(value) : value.toFixed(2);
      element.textContent = prefix + display + suffix;

      if (progress < 1) {
        requestAnimationFrame(tick);
      }
    }

    requestAnimationFrame(tick);
  }

  function bindMetricCounters() {
    App.qsa("[data-count-to]").forEach(animateNumber);
  }

  function bindRefreshCards() {
    App.qsa("[data-refresh-section]").forEach(function (button) {
      App.on(button, "click", async function () {
        var sectionId = button.dataset.refreshSection;
        var endpoint = button.dataset.endpoint;
        var section = document.getElementById(sectionId);

        if (!section || !endpoint) {
          return;
        }

        App.setButtonLoading(button, true, "Refreshing...");

        try {
          var data = await App.apiFetch(endpoint);
          section.dispatchEvent(new CustomEvent("section:data", { detail: data }));
          App.showAlert("Dashboard data refreshed.", "success");
        } catch (error) {
          App.showAlert(error.message, "danger");
        } finally {
          App.setButtonLoading(button, false);
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindMetricCounters();
    bindRefreshCards();
  });
})();
