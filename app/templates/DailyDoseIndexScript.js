const bookmark = document.getElementById("bookmark");
const addAffirmation = document.getElementById("add-affirmation");
const categorySelected = document.getElementById("category");
const affirmationInput = document.getElementById("affirmation-input");

const positiveMessages = [
    {
        category: "self-worth",
        affirmation: `This moment doesn't define you. Better days are coming.`
    },
    {
        category: "lost",
        affirmation: `It's okay to not have everything figured out right now.. You're doing your best, and that's enough.`
    },
    {
        category: "self-worth",
        affirmation: `"You're not behind. Everyone's journey is different.`
    },
    {
        category: "healing",
        affirmation: `Healing is not linear. Every step counts.`
    },
    {
        category: "lost",
        affirmation: `Who you are becoming is more important than who others expect you to be.`
    }
];

categorySelected.addEventListener("change", (event) => {
    const category = event.target.value;
    let filteredAffirmation = [];
    if (!category) {    //not sure if this is the right implementation if the user has not selected any category
        filteredAffirmation = positiveMessages.affirmation;
    }
    else {
        filteredAffirmation = positiveMessages.filter(message => message.category === category);
    }
    let randomNum = Math.floor(Math.random() * filteredAffirmation.length) + 1;
    return filteredAffirmation[randomNum];
})

function dailyAffirmation() {
    let randomNum = Math.floor(Math.random() * positiveMessages.length) + 1;
    return positiveMessages[randomNum];
}

    const fWord = /(?:^|\s)f[u0o]ck(?:$|\s)/i;
    const bWord = /(?:^|\s)b[i!1]tch(?:$|\s)/i;
    const pWord = /(?:^|\s)pr[i!1]ck(?:$|\s)/i;

    const inappropriateWordList = [fWord, bWord, pWord];

    const isValid = (str) => inappropriateWordList.some((regex) => regex.test(msg))


addAffirmation.addEventListener("click", () => {
    if (affirmationInput.value.trim() === "") {
        alert("Please enter your desired affirmation.");
        return;
    }
    isValid(affirmationInput);
    if (isValid) {
        "Your affirmation has been added to our list, thank you."; 
        positiveMessages.push(affirmationInput);
    }
    else {
        "Sorry, curse words are not permitted as an affirmation.";
    } 
});