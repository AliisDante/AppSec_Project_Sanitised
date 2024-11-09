function add_image_previews(file_list, image_container) {
  let preview_image_template = document.querySelector(".preview_image_template");
  Array.from(file_list).forEach((file) => {
    let new_preview_image_elem = preview_image_template.cloneNode(true);
    new_preview_image_elem.classList.add("preview_image");
    new_preview_image_elem.classList.remove("preview_image_template");
    new_preview_image_elem.classList.remove("hidden");
    new_preview_image_elem.src = URL.createObjectURL(file);
    image_container.appendChild(new_preview_image_elem);
  });
}

function generate_like_url(post_id) {
  return window.location.origin + `/posts/${post_id}/like`;
}

function send_like(post_id) {
  let url = generate_like_url(post_id);
  fetch(url, {method: "post"}).then(() => window.location.reload(), () => window.location.reload())
}

document.addEventListener("DOMContentLoaded", () => {
  let posts = document.querySelectorAll(".post");
  posts.forEach((post_elem) => {
    let like_button = post_elem.querySelector(".like_button");
    let post_id = post_elem.getAttribute("data-post-id");
    like_button.addEventListener("click", () => {
      send_like(post_id);
    })
  });

  let image_container = document.querySelector(".new_post_images_container");
  let file_input = document.querySelector(".new_image_file");
  file_input.addEventListener("input", () => {
    let images = image_container.querySelectorAll("img.preview_image");
    Array.from(images).forEach((preview_image_elem) => preview_image_elem.remove());
    add_image_previews(file_input.files, image_container);
  });
});
