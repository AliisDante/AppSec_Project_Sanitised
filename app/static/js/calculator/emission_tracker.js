function create_new_day_chip_elem(day_elem, data, info) {
  let day_chip_template_elem = document.querySelector(".day-chip-template");

  let new_day_chip_elem = day_chip_template_elem.cloneNode(true);

  new_day_chip_elem.innerText = data;
  new_day_chip_elem.id = info;
  new_day_chip_elem.classList.remove("day-chip-template");
  new_day_chip_elem.style.display = "inherit";

  day_elem.append(new_day_chip_elem);
}

function setup_chip_elem(chip_elem) {
  chip_elem.setAttribute("draggable", true);
  let chip_elem_text = chip_elem.innerText;
  let chip_elem_info = chip_elem.id;
  chip_elem.addEventListener("dragstart", (e) => {
    e.dataTransfer.setData("text/plain", `${chip_elem_text}|${chip_elem_info}`);
  });
}

function setup_day_elem(day_elem) {
  day_elem.addEventListener("dragenter", (e) => e.preventDefault());
  day_elem.addEventListener("dragover", (e) => e.preventDefault());
  day_elem.addEventListener("drop", (e) => {
    const data = e.dataTransfer.getData("text/plain").split("|")[0];
    const info = e.dataTransfer.getData("text/plain").split("|")[1];
    create_new_day_chip_elem(day_elem, data, info);
  });
}

let api_version = "v2";

document.addEventListener("DOMContentLoaded", () => {
  let day_elems = document.querySelectorAll(".day-activity");
  day_elems.forEach(setup_day_elem);

  let chip_elems = document.querySelectorAll(".selection-chip");
  chip_elems.forEach((element) => setup_chip_elem(element));

  let reset_button = document.querySelector(".reset-button");
  reset_button.addEventListener("click", () => window.location.reload());

  let generate_button = document.querySelector(".generate-button");
  generate_button.addEventListener("click", () => submit_activities(gather_activities(),api_version));
});

function gather_activities(){
  activities_nodes = document.querySelectorAll(".day-activity span");
  compiled_activities = {
    "activities": []
  }

  for (i=0; i<activities_nodes.length; i++){
    compiled_activities["activities"].push({
      "item": activities_nodes[i].innerText,
      "category": activities_nodes[i].id.split("-")[0],
      "emission": Number(activities_nodes[i].id.split("-")[1])
    })
  }

  console.log(compiled_activities);

  return compiled_activities
}