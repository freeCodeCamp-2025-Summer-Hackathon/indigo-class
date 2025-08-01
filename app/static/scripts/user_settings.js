const modal = document.querySelector(".modal__bg");
const modalContent = document.querySelector(".modal__content");

document.querySelectorAll("[data-type]").forEach(trigger => {
    trigger.addEventListener("click", function(event) {
        const type = event.currentTarget.getAttribute("data-type");

        modalContent.innerHTML = generateModalContent(type);
        modal.style.display = "flex";

        //close btn
        modalContent.querySelector(".close").addEventListener("click", function() {
            modal.style.display = "none";
        });

        modalContent.querySelector(".cancel").addEventListener("click", function() {
            modal.style.display = "none";
        })
    });
});

// alternate close btn
window.addEventListener("click", function(event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
});

function generateModalContent(type) {
    if (type === "change__dname") {
        return `
        <span class="close">&times;</span>
        <form class="form__group dname" method="POST" action="${urls.updateProfile}">

            <label for="change__dname">New Display Name:</label>
            <input type="text" id="change__dname" name="first_name" required>

            <label for="dname__password">Current Password:</label>
            <input type="password" id="dname__password" name="password" required>

            <button type="submit" class="submit">Submit</button>
        </form>
        `
    }
    else if (type === "change__pic") {
        return `
        <span class="close">&times;</span>
        <form class="form__group pic " method="POST" action="${urls.updateProfile}">
            <label for="change__pic">Change your profile picture</label>
            <input type="file" id="change__pic" accept="image/*" required>

            <button type="submit" class="submit">Upload</button>
        </form>
        `
    }
    else if (type === "delete") {
        return `
        <span class="close">&times;</span>
        <form class="form__group delete" method="POST" action="${urls.deleteUser}">
            <p class="paragraph">Are you sure you really want to delete your account?</p>

            <label for="delete__account__password">Current Password:</label>
            <input type="password" id="delete__account__password" name="password" required>
            
            <button type="submit" class="logout__delete">Yes</button>
            <button type="button" class="cancel">No</button>
        </form>
        `
    }
}