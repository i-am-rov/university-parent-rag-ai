(function () {
  "use strict";

  function bindTableFilter() {
    App.qsa("[data-table-filter]").forEach(function (input) {
      var tableId = input.dataset.tableFilter;
      var table = document.getElementById(tableId);

      if (!table) {
        return;
      }

      App.on(input, "input", function () {
        var query = input.value.trim().toLowerCase();

        App.qsa("tbody tr", table).forEach(function (row) {
          var text = row.textContent.toLowerCase();
          row.hidden = query && !text.includes(query);
        });
      });
    });
  }

  function bindFeeCalculator() {
    var form = App.qs("[data-fee-calculator]");
    if (!form) {
      return;
    }

    App.on(form, "input", function () {
      var tuition = Number(form.elements.tuition_fee ? form.elements.tuition_fee.value : 0);
      var registration = Number(form.elements.registration_fee ? form.elements.registration_fee.value : 0);
      var lab = Number(form.elements.lab_fee ? form.elements.lab_fee.value : 0);
      var other = Number(form.elements.other_fee ? form.elements.other_fee.value : 0);
      var waiver = Number(form.elements.waiver_percentage ? form.elements.waiver_percentage.value : 0);
      var paid = Number(form.elements.paid_amount ? form.elements.paid_amount.value : 0);
      var output = App.qs("[data-fee-output]");

      if (!output) {
        return;
      }

      var waiverAmount = tuition * (waiver / 100);
      var payableTuition = tuition - waiverAmount;
      var total = registration + payableTuition + lab + other;
      var due = total - paid;

      output.textContent = due.toLocaleString("en-US", {
        maximumFractionDigits: 2
      });
    });
  }

  function bindProfileTabs() {
    var tabs = App.qsa("[data-profile-tab]");
    if (!tabs.length) {
      return;
    }

    tabs.forEach(function (tab) {
      App.on(tab, "click", function () {
        tabs.forEach(function (item) {
          item.classList.remove("active");
          item.setAttribute("aria-selected", "false");
        });

        App.qsa("[data-profile-panel]").forEach(function (panel) {
          panel.hidden = panel.id !== tab.dataset.profileTab;
        });

        tab.classList.add("active");
        tab.setAttribute("aria-selected", "true");
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindTableFilter();
    bindFeeCalculator();
    bindProfileTabs();
  });
})();
