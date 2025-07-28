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

// Function to show flash messages
function showFlashMessage(message, category = 'error') {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${category}`;
  alertDiv.innerHTML = `
    <p>${message}</p>
    <button class="alert__btn" type="button" onclick="this.parentElement.remove()" aria-label="Close alert">✕</button>
  `;

  // Insert at the beginning of main content
  const main = document.querySelector('main');
  if (main) {
    main.insertBefore(alertDiv, main.firstChild);
  }

  // Auto-remove after 5 seconds
  setTimeout(() => {
    if (alertDiv.parentElement) {
      alertDiv.remove();
    }
  }, 5000);
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
  const pinButton = document.querySelector("#affirmation-generator .pin-affirmation");

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
              // Disable pin button if no affirmation found
              if (pinButton) {
                pinButton.disabled = true;
                pinButton.onclick = null;
              }
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

        // Update pin button with new affirmation ID
        if (pinButton && data.affirmation_id) {
          pinButton.disabled = false;
          // For now, we'll assume it's not pinned and show the pin button
          // In a more advanced implementation, we could check the pin status
          pinButton.innerHTML = '&plus;';
          pinButton.setAttribute('aria-label', 'Pin');
          pinButton.onclick = () => handleAffirmationPin(data.affirmation_id);
        }
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
  const dialogCategoryId = document.querySelector("#category-edit-dialog #dialog-category-id-edit");

  dialogCategoryName.value = categoryName;
  dialogCategoryId.value = categoryId;

  dialog.showModal();
}

// Global variable to store selected categories
let selectedCategories = [];

function addCategoryToAffirmation() {
  const categorySelect = document.getElementById('dialog-assign-category');
  const categoryId = categorySelect.value;
  const categoryName = categorySelect.options[categorySelect.selectedIndex].text;

  if (!categoryId) {
    alert('Please select a category first.');
    return;
  }

  // Check if category is already added
  if (selectedCategories.some(cat => cat.id === categoryId)) {
    alert('This category is already added.');
    return;
  }

  // Add to selected categories
  selectedCategories.push({ id: categoryId, name: categoryName });

  // Update the display
  updateCategoriesDisplay();

  // Reset select
  categorySelect.value = '';
}

function removeCategoryFromAffirmation(categoryId) {
  selectedCategories = selectedCategories.filter(cat => cat.id !== categoryId);
  updateCategoriesDisplay();
}

function updateCategoriesDisplay() {
  const categoriesList = document.getElementById('dialog-categories-added');
  categoriesList.innerHTML = '';

  selectedCategories.forEach(category => {
    const li = document.createElement('li');
    li.innerHTML = `
      <span>${category.name}</span>
      <button type="button" class="btn btn--danger" onclick="removeCategoryFromAffirmation('${category.id}')">&times;</button>
    `;
    categoriesList.appendChild(li);
  });
}

function showEditAffirmationDialog(affirmationId, affirmationText, categoriesJson) {
  const dialog = document.getElementById("affirmation-dialog");
  const dialogAffirmationId = document.querySelector("#affirmation-dialog #dialog-affirmation-id");
  const dialogAffirmationText = document.querySelector("#affirmation-dialog #dialog-affirmation-text");

  dialogAffirmationId.value = affirmationId;
  dialogAffirmationText.value = affirmationText;

  // Reset selected categories
  selectedCategories = [];

  // Parse and set current categories if editing
  if (categoriesJson && categoriesJson !== "[]") {
    try {
      const categoryIds = JSON.parse(categoriesJson);
      // We need to get the category names from the select options
      const categorySelect = document.getElementById('dialog-assign-category');
      categoryIds.forEach(catId => {
        for (let option of categorySelect.options) {
          if (option.value === catId.toString()) {
            selectedCategories.push({ id: catId.toString(), name: option.text });
            break;
          }
        }
      });
    } catch (e) {
      console.error('Error parsing categories:', e);
    }
  }

  // Update the display
  updateCategoriesDisplay();

  dialog.showModal();
}

function showCreateCategoryDialog() {
  const dialog = document.getElementById("category-create-dialog");
  dialog.showModal();
}

function showAffirmationDialog() {
  const dialog = document.getElementById("affirmation-dialog");
  // Reset selected categories for new affirmation
  selectedCategories = [];
  updateCategoriesDisplay();
  dialog.showModal();
}

function closeDialog(dialogId) {
  const dialog = document.getElementById(dialogId);
  dialog.close();
}

function handleCategoryDialogSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  const categoryId = formData.get('category_id');
  const categoryName = formData.get('category_name');

  if (categoryId) {
    // Edit existing category
    fetch(`/categories/edit/${categoryId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: categoryName })
    })
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          showFlashMessage('Error: ' + data.error, 'error');
          return;
        }
        showFlashMessage('Category updated successfully!', 'success');
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      })
      .catch(error => {
        console.error('Error:', error);
        showFlashMessage('An error occurred while updating the category.', 'error');
      });
  } else {
    // Create new category
    fetch('/categories/add', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: categoryName })
    })
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          showFlashMessage('Error: ' + data.error, 'error');
          return;
        }
        showFlashMessage('Category created successfully!', 'success');
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      })
      .catch(error => {
        console.error('Error:', error);
        showFlashMessage('An error occurred while creating the category.', 'error');
      });
  }

  closeDialog(form.closest('dialog').id);
}

function handleCategoryDelete(categoryId) {
  if (confirm('Are you sure you want to delete this category?')) {
    fetch(`/categories/delete/${categoryId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          showFlashMessage('Error: ' + data.error, 'error');
          return;
        }
        showFlashMessage('Category deleted successfully!', 'success');
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      })
      .catch(error => {
        console.error('Error:', error);
        showFlashMessage('An error occurred while deleting the category.', 'error');
      });
  }
}

function handleAffirmationDelete(affirmationId) {
  if (confirm('Are you sure you want to delete this affirmation?')) {
    fetch(`/affirmations/delete/${affirmationId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          alert('Error: ' + data.error);
          return;
        }
        window.location.reload();
      })
      .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while deleting the affirmation.');
      });
  }
}

function handleAffirmationPin(affirmationId) {
  fetch(`/affirmations/action/pin`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ affirmationId })
  })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        // Show flash message for pin limit
        if (data.error.includes('pin already limited')) {
          showFlashMessage('You have reached the maximum limit of 3 pinned affirmations. Please unpin another affirmation first.', 'error');
        } else {
          showFlashMessage('Error: ' + data.error, 'error');
        }
        return;
      }
      // Show success message and refresh the page
      showFlashMessage('Affirmation pinned successfully!', 'success');
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    })
    .catch(error => {
      console.error('Error:', error);
      showFlashMessage('An error occurred while pinning the affirmation.', 'error');
    });
}

function handleAffirmationUnpin(affirmationId) {
  fetch(`/affirmations/action/delete`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ affirmationId })
  })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        showFlashMessage('Error: ' + data.error, 'error');
        return;
      }
      // Show success message and refresh the page
      showFlashMessage('Affirmation unpinned successfully!', 'success');
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    })
    .catch(error => {
      console.error('Error:', error);
      showFlashMessage('An error occurred while unpinning the affirmation.', 'error');
    });
}

function handleAffirmationDialogSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  const affirmationId = formData.get('affirmation_id');
  const affirmationText = formData.get('affirmation_text');

  // Get selected category IDs
  const selectedCategoryIds = selectedCategories.map(cat => cat.id);

  if (affirmationId) {
    // Edit existing affirmation
    fetch(`/affirmations/edit/${affirmationId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        affirmation_text: affirmationText,
        category_ids: selectedCategoryIds
      })
    })
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          alert('Error: ' + data.error);
          return;
        }
        window.location.reload();
      })
      .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the affirmation.');
      });
  } else {
    // Create new affirmation
    fetch('/affirmations/add', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        affirmation_text: affirmationText,
        category_ids: selectedCategoryIds
      })
    })
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          alert('Error: ' + data.error);
          return;
        }
        window.location.reload();
      })
      .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while creating the affirmation.');
      });
  }

  closeDialog(form.closest('dialog').id);
}