// BlueCart JavaScript - small and beginner-friendly.
document.addEventListener("DOMContentLoaded", function () {

  // 1. Mobile menu: open and close the navigation links.
  var navToggle = document.getElementById("nav-toggle");
  var mainNav = document.getElementById("main-nav");
  if (navToggle && mainNav) {
    navToggle.addEventListener("click", function () {
      var isOpen = mainNav.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
  }

  // 2. Messages: close button, and success messages fade away by themselves.
  document.querySelectorAll(".message").forEach(function (message) {
    var closeButton = message.querySelector(".message-close");
    if (closeButton) {
      closeButton.addEventListener("click", function () { message.remove(); });
    }
    if (message.classList.contains("message-success")) {
      setTimeout(function () { message.remove(); }, 5000);
    }
  });

  // 3. Quantity buttons (+ and -). The server still checks stock again,
  //    so this is only for convenience.
  document.querySelectorAll("[data-qty]").forEach(function (box) {
    var input = box.querySelector("input");
    box.querySelectorAll("[data-step]").forEach(function (button) {
      button.addEventListener("click", function () {
        var step = parseInt(button.dataset.step, 10);
        var min = input.min === "" ? 1 : parseInt(input.min, 10);
        var max = input.max === "" ? 99 : parseInt(input.max, 10);
        var value = parseInt(input.value, 10);
        if (isNaN(value)) { value = min; }
        input.value = Math.min(max, Math.max(min, value + step));
      });
    });
  });

  // 4. Checkout: stop double-clicks from sending the order twice.
  var checkoutForm = document.getElementById("checkout-form");
  var placeOrderButton = document.getElementById("place-order-btn");
  if (checkoutForm && placeOrderButton) {
    checkoutForm.addEventListener("submit", function () {
      placeOrderButton.disabled = true;
      placeOrderButton.textContent = "Placing your order...";
    });
  }
});
