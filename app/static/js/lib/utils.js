// app/static/js/lib/utils.js
function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}
// (Then use this function if you want to conditionally join class names.)
