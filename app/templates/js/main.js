mdc = require("material-components-web");

mdc.autoInit();

const drawer = document.getElementById('nav-drawer').MDCDrawer;
const top_app_bar = document.getElementById('app-bar').MDCTopAppBar;
top_app_bar.setScrollTarget(document.getElementById('main-content'));
top_app_bar.listen('MDCTopAppBar:nav', () => {
  drawer.open = !drawer.open;
});

const snackbar = document.querySelector('.mdc-snackbar');
if (snackbar) {
  snackbar.MDCSnackbar.open();
  let snackbar_dismiss_button = snackbar.querySelector('button.mdc-snackbar__dismiss');
  snackbar_dismiss_button.addEventListener('click', () => {
    snackbar.MDCSnackbar.close();
  });
}
