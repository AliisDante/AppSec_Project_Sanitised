document.addEventListener("DOMContentLoaded", () => {
  let remember_switch = document.querySelector(".remember_switch");
  let remember_checkbox = document.querySelector(".remember_checkbox");
  remember_switch.addEventListener("click", () => {
    remember_checkbox.checked = !remember_checkbox.checked;
  });
});
