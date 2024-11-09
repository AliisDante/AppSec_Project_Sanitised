function create_new_day_chip_elem(day_elem, data) {
  let day_chip_template_elem = document.querySelector(".day-chip-template");

  let new_day_chip_elem = day_chip_template_elem.cloneNode(true);

  new_day_chip_elem.innerText = data;
  new_day_chip_elem.classList.remove("day-chip-template");
  new_day_chip_elem.style.display = "inherit";

  day_elem.append(new_day_chip_elem);
}

function setup_chip_elem(chip_elem) {
  chip_elem.setAttribute("draggable", true);
  let chip_elem_text = chip_elem.innerText;
  chip_elem.addEventListener("dragstart", (e) => {
    e.dataTransfer.setData("text/plain", chip_elem_text);
  });
}

function setup_day_elem(day_elem) {
  day_elem.addEventListener("dragenter", (e) => e.preventDefault());
  day_elem.addEventListener("dragover", (e) => e.preventDefault());
  day_elem.addEventListener("drop", (e) => {
    const data = e.dataTransfer.getData("text/plain");
    create_new_day_chip_elem(day_elem, data);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  let day_elems = document.querySelectorAll(".day-activity");
  day_elems.forEach(setup_day_elem);

  let chip_elems = document.querySelectorAll(".selection-chip");
  chip_elems.forEach((element) => setup_chip_elem(element));

  let reset_button = document.querySelector(".reset-button");
  reset_button.addEventListener("click", () => window.location.reload());
});
