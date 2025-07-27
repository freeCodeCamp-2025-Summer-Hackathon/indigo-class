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

// To top button
document.addEventListener("DOMContentLoaded", function () {
  const scrollToTopBtn = document.querySelector(".totop__button");

  // Show/hide button on scroll
  window.addEventListener("scroll", function () {
    scrollToTopBtn.style.display = window.scrollY > 50 ? "block" : "none";
  });

  // Load initial random affirmation
  const affirmationElement = document.getElementById("random-affirmation");
  if (affirmationElement) {
    getRandomAffirmation();
  }

  // Add change event listener to category select
  const categorySelect = document.getElementById("category-select");
  if (categorySelect) {
    categorySelect.addEventListener("change", function () {
      getRandomAffirmation();
    });
  }
});

// Scroll to top on click
function toTop() {
  window.scrollTo(0, 0);
};

function saveAffirmation(affirmationId) {
  fetch(`/affirmations/save`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ affirmationId }),
  });
}

let randomAffirmationRequestId = 0;

function getRandomAffirmation() {
  const affirmationElement = document.getElementById("random-affirmation");
  const affirmCatElement = document.getElementById("rand-affirm-cat");
  const categorySelect = document.getElementById("category-select");

  if (affirmationElement) {
    const categoryId = categorySelect ? categorySelect.value : "all";
    const oldAffirmation = affirmationElement.textContent;
    const oldCategories = affirmCatElement.textContent;

    // Increment request id
    const thisRequestId = ++randomAffirmationRequestId;

    fetch(`/affirmations/random?category=${categoryId}`)
      .then((response) => {
        if (!response.ok) {
          if (response.status === 429) {
            throw new Error("Please wait 10 seconds for next request");
          }
          if (response.status === 404 || response.status === 400) {
            if (thisRequestId === randomAffirmationRequestId) {
              affirmationElement.textContent = "No affirmations found";
              affirmCatElement.textContent = "No affirmations found in this category";
            }
            return null;
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (!data) return;
        if (thisRequestId !== randomAffirmationRequestId) return; // Only update if this is the latest request
        if (data.error) {
          throw new Error(data.error);
        }
        affirmationElement.textContent = data.affirmation;
        const categoriesText = Array.isArray(data.categories)
          ? data.categories.join(", ")
          : data.categories;
        affirmCatElement.textContent = categoriesText;
      })
      .catch((error) => {
        if (thisRequestId !== randomAffirmationRequestId) return;
        console.error("Error fetching random affirmation:", error);
        if (error.message === "Please wait 10 seconds for next request") {
          const errorDiv = document.createElement("div");
          errorDiv.textContent = error.message;
          errorDiv.style.color = "red";
          errorDiv.style.fontSize = "0.8em";
          affirmationElement.parentNode.insertBefore(errorDiv, affirmationElement.nextSibling);
          setTimeout(() => errorDiv.remove(), 1000);
        } else {
          affirmationElement.textContent = oldAffirmation;
        }
        affirmCatElement.textContent = oldCategories;
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
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        console.error("Error:", data.error);
        return;
      }

      // Refresh the page to show updated state
      window.location.reload();
    })
    .catch(error => {
      console.error("Error updating action:", error);
    });
}

function showEditCategoryDialog(categoryId, categoryName) {
  const dialog = document.getElementById("category-edit-dialog");
  const dialogCategoryName = document.querySelector("#category-edit-dialog #dialog-category-name");
  const dialogCategoryId = document.querySelector("#category-edit-dialog #dialog-category-id");

  dialogCategoryName.value = categoryName;
  dialogCategoryId.value = categoryId;

  dialog.showModal();
}

function showCreateCategoryDialog() {
  const dialog = document.getElementById("category-create-dialog");
  dialog.showModal();
}

function showAffirmationDialog() {
  const dialog = document.getElementById("affirmation-dialog");
  dialog.showModal();
}

function closeDialog(dialogId) {
  const dialog = document.getElementById(dialogId);
  dialog.close();
}