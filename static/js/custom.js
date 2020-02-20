function add_css_class(filter, ...classes) {
  document.querySelectorAll(filter).forEach(function(item) {
    item.classList.add(...classes);
  });
}