document.addEventListener("DOMContentLoaded", () => {
  let delay_for_input_update = 100;
  let log_type_select_interface_options = document.querySelectorAll(".log_type_select_interface_option");
  let log_type_select = document.querySelector(".log_type_select");

  Array.from(log_type_select_interface_options).forEach((option_elem) => {
    option_elem.addEventListener("click", () => {
      setTimeout(() => {
        let selected_log_type = log_type_select.value;
        if (selected_log_type == "") {
          selected_log_type = "all";
        }
        let redirect_url = `${window.location.origin}/logs/${selected_log_type}`
        window.location = redirect_url;
      }, delay_for_input_update);
    });
  });
});
