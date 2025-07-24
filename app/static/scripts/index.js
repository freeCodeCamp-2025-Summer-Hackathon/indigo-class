// Toggle between showing and hiding the navigation menu links when the user clicks on the hamburger menu / bar icon
function navDropdown() {
  const navDropdown = document.getElementById("nav__dropdown");
  if (navDropdown.style.visibility === "visible") {
    navDropdown.style.visibility = "hidden";
  } else {
    navDropdown.style.visibility = "visible";
  }
}

// Logout button in admin desktop
function navAdminDesktopLogOut() {
  const navLogoutAdminDesktopMenu = document.getElementById("nav__logout--desktopadmin");
  if (navLogoutAdminDesktopMenu.style.visibility === "visible") {
    navLogoutAdminDesktopMenu.style.visibility = "hidden";
  } else {
    navLogoutAdminDesktopMenu.style.visibility = "visible";
  }
}

// To top button in footer
function toTop() {
  window.scrollTo(0, 0);
}

function saveAffirmation(affirmationId) {
  fetch(`/affirmations/save`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ affirmationId }),
  });
}


function getRandomAffirmation() {
  const affirmationElement = document.getElementById("random-affirmation");
  if (affirmationElement) {
    affirmationElement.textContent = "Loading...";
    fetch("/affirmations/random")
      .then((response) => response.json())
      .then((data) => {
        const affirmation = data.affirmation;
        affirmationElement.textContent = affirmation;
      })
      .catch(() => {
        affirmationElement.textContent = "Failed to load affirmation.";
      });
  }
}

function selectAffirmationCategory(affirmationId, categoryId) {
  fetch(`/affirmations/select-category`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ affirmationId, categoryId })
  })
}

function updateActionType(affirmationId, actionType) {
  fetch(`/affirmations/action/${actionType}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ affirmationId })
  })
}