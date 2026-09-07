/**
 * AI Recipe Generator - Skolprojekt JavaScript (script.js)
 * 
 * Detta skript hanterar:
 * 1. Formulärinlämning utan att ladda om sidan (AJAX via fetch API).
 * 2. Visning av laddningsindikator medan servern skapar receptet.
 * 3. Dynamisk presentation av receptet i webbläsaren.
 * 4. Snabbval för vanliga önskemål (t.ex. vegetariskt, starkt).
 */

document.addEventListener("DOMContentLoaded", () => {
    // Hämta viktiga HTML-element från sidan
    const form = document.getElementById("recipe-form");
    const ingredientsInput = document.getElementById("ingredients");
    const servingsInput = document.getElementById("servings");
    const preferencesInput = document.getElementById("preferences");
    const submitBtn = document.getElementById("submit-btn");
    const loadingSpinner = document.getElementById("loading-spinner");
    const errorMessage = document.getElementById("error-message");
    const recipeResult = document.getElementById("recipe-result");

    // Element för att visa receptinformation
    const recipeTitle = document.getElementById("recipe-title");
    const recipeDescription = document.getElementById("recipe-description");
    const recipeServings = document.getElementById("recipe-servings");
    const recipeCooktime = document.getElementById("recipe-cooktime");
    const recipePreferences = document.getElementById("recipe-preferences");
    const recipeIngredientsList = document.getElementById("recipe-ingredients-list");
    const recipeInstructionsList = document.getElementById("recipe-instructions-list");
    const recipeTipText = document.getElementById("recipe-tip-text");

    // -------------------------------------------------------------
    // 1. Hantera klick på snabbval (taggar för önskemål)
    // -------------------------------------------------------------
    const tagButtons = document.querySelectorAll(".tag-btn");
    tagButtons.forEach(button => {
        button.addEventListener("click", () => {
            const tagValue = button.getAttribute("data-tag");
            const currentVal = preferencesInput.value.trim();

            if (currentVal.length === 0) {
                preferencesInput.value = tagValue;
            } else if (!currentVal.toLowerCase().includes(tagValue.toLowerCase())) {
                // Lägg till med komma om det redan finns text
                preferencesInput.value = `${currentVal}, ${tagValue}`;
            }
            preferencesInput.focus();
        });
    });

    // -------------------------------------------------------------
    // 2. Hantera formulärinskickning (Generera recept)
    // -------------------------------------------------------------
    form.addEventListener("submit", async (event) => {
        // Förhindra att webbläsaren laddar om sidan
        event.preventDefault();

        // Nollställ eventuella tidigare felmeddelanden
        hideError();

        // Hämta värden från fälten
        const ingredients = ingredientsInput.value.trim();
        const servings = parseInt(servingsInput.value, 10) || 2;
        const preferences = preferencesInput.value.trim();

        // Enkel validering på klientsidan
        if (!ingredients) {
            showError("Vänligen ange vilka ingredienser du har hemma.");
            return;
        }

        // Sätt gränssnittet i "laddar"-läge
        setLoading(true);

        try {
            // Skicka en POST-förfrågan till Flask-serverns API
            const response = await fetch("/api/generate-recipe", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    ingredients: ingredients,
                    servings: servings,
                    preferences: preferences
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                // Om servern returnerade ett fel
                throw new Error(data.error || "Ett oväntat fel uppstod vid receptgenereringen.");
            }

            // Visa det genererade receptet
            displayRecipe(data.recipe);

        } catch (error) {
            console.error("Fel vid anrop till receptservern:", error);
            showError(error.message || "Kunde inte ansluta till servern. Kontrollera att Flask körs i terminalen.");
        } finally {
            // Återställ knapp och dölj laddningssymbol oavsett om det lyckades eller misslyckades
            setLoading(false);
        }
    });

    // -------------------------------------------------------------
    // 3. Funktion för att rendera receptet i HTML
    // -------------------------------------------------------------
    function displayRecipe(recipe) {
        // Fyll i titel och beskrivning
        recipeTitle.textContent = recipe.title;
        recipeDescription.textContent = recipe.description;
        recipeServings.textContent = `${recipe.servings} portioner`;
        recipeCooktime.textContent = `${recipe.cook_time} (förb: ${recipe.prep_time})`;
        recipePreferences.textContent = recipe.preferences || "Inga";

        // Töm och fyll ingredienslistan
        recipeIngredientsList.innerHTML = "";
        recipe.ingredients.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            recipeIngredientsList.appendChild(li);
        });

        // Töm och fyll instruktionslistan
        recipeInstructionsList.innerHTML = "";
        recipe.instructions.forEach(step => {
            const li = document.createElement("li");
            li.textContent = step;
            recipeInstructionsList.appendChild(li);
        });

        // Fyll i kockens tips
        recipeTipText.textContent = recipe.chef_tip;

        // Gör receptkortet synligt och skrolla mjukt dit
        recipeResult.classList.remove("hidden");
        recipeResult.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // -------------------------------------------------------------
    // 4. Hjälpfunktioner för UI-tillstånd
    // -------------------------------------------------------------
    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            submitBtn.querySelector(".btn-text").textContent = "Skapar recept...";
            loadingSpinner.classList.remove("hidden");
        } else {
            submitBtn.disabled = false;
            submitBtn.querySelector(".btn-text").textContent = "Generera recept";
            loadingSpinner.classList.add("hidden");
        }
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove("hidden");
    }

    function hideError() {
        errorMessage.textContent = "";
        errorMessage.classList.add("hidden");
    }
});
