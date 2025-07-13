// Toggle between showing and hiding the navigation menu links when the user clicks on the hamburger menu / bar icon
function navDropdown() {
    const navDropdown = document.getElementById("nav__dropdown");
    if (navDropdown.style.visibility === "visible") {
        navDropdown.style.visibility = "hidden";
    } else {
        navDropdown.style.visibility = "visible";
    }
  } 

// To top button in footer
function toTop() {
    window.scrollTo(0, 0);
  } 