// Toggle between showing and hiding the navigation menu links when the user clicks on the hamburger menu / bar icon
function navDropdown() {
  const navDropdown = document.getElementById("nav__dropdown");
  if (navDropdown.style.visibility === "visible") {
    navDropdown.style.visibility = "hidden";
  } else {
    navDropdown.style.visibility = "visible";
  }
}

// Logout button in admin desktop sidebar
function navAdminDesktopLogOut() {
  const navLogoutAdminDesktopMenu = document.getElementById("nav__sidebar--logout");
  if (navLogoutAdminDesktopMenu.style.visibility === "visible") {
    navLogoutAdminDesktopMenu.style.visibility = "hidden";
  } else {
    navLogoutAdminDesktopMenu.style.visibility = "visible";
  }
}

// Force menu to be visible in admin desktop sidebar when resizing


// To top button
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
  const affirmCatElement = document.getElementById("rand-affirm-cat");
  if (affirmationElement) {
    affirmationElement.textContent = "Loading...";
    fetch("/affirmations/random")
      .then((response) => response.json())
      .then((data) => {
        console.log("Affirmation Data:", data);
        const affirmation = data.affirmation;
        affirmationElement.textContent = affirmation;
        affirmCatElement.textContent = affirmation.categories;
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