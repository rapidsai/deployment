document.addEventListener("DOMContentLoaded", function () {
  // Simplify tags and add class for styling
  // It's not possible to control these attributes in Sphinx otherwise we would
  Array.from(document.getElementsByClassName("sd-badge")).forEach((tag) => {
    tag.setAttribute("aria-label", tag.innerHTML);
    try {
      tag
        .getAttribute("aria-label")
        .split("/")
        .forEach((subtag) => tag.classList.add(`tag-${subtag}`));
    } catch (err) {}

    if (tag.innerHTML.includes("/")) {
      tag.innerHTML = tag.innerHTML.split("/").slice(1).join("/");
    }
  });
});
