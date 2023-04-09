    document.addEventListener("DOMContentLoaded", function () {
        let selectedKeywords = new Set(JSON.parse(localStorage.getItem("selectedKeywords")) || []);
        let colorMapping = JSON.parse(localStorage.getItem("colorMapping")) || {};
        let colors = ['#999999', '#f781bf', '#a65628', '#ffff33', '#ff7f00', '#984ea3', '#4daf4a', '#377eb8', '#e41a1c'];
        let availableColors = colors.filter(color => !Object.values(colorMapping).includes(color));

        function updateCheckboxes(value, isChecked) {
            document.querySelectorAll(".keyword-checkbox").forEach(function (checkbox) {
                if (checkbox.value === value) {
                    checkbox.checked = isChecked;
                }
            });
        }

        function storeSelectedKeywords() {
            localStorage.setItem("selectedKeywords", JSON.stringify(Array.from(selectedKeywords)));
        }

        // Restore the checked state of checkboxes from localStorage
        selectedKeywords.forEach(function (keyword) {
            updateCheckboxes(keyword, true);
        });

        document.querySelectorAll(".keyword-checkbox").forEach(function (checkbox) {
            checkbox.addEventListener("change", function () {
                const isChecked = checkbox.checked;

                if (isChecked) {
                    selectedKeywords.add(checkbox.value);
                } else {
                    selectedKeywords.delete(checkbox.value);
                    removeColor(checkbox.value);
                }

                if (selectedKeywords.size > 9) {
                    checkbox.checked = false;
                    selectedKeywords.delete(checkbox.value);
                    removeColor(checkbox.value);
                    isChecked = false;
                }

                updateCheckboxes(checkbox.value, isChecked);
                storeSelectedKeywords();

                // Update checkbox colors
                updateCheckboxColors();

                // Reload the page with the selected keywords as a query parameter
                const url = new URL(window.location.href);
                url.searchParams.set("selected_keywords", Array.from(selectedKeywords).join(','));
                window.location.href = url.toString();
            });
        });

        updateCheckboxes();

        function getColor(value) {
            if (!colorMapping[value]) {
                const color = availableColors.pop(); // Get the last available color
                colorMapping[value] = color;
                localStorage.setItem("colorMapping", JSON.stringify(colorMapping)); // Store colorMapping in localStorage
            }
            return colorMapping[value];
        }

        function removeColor(value) {
            if (colorMapping[value]) {
                availableColors.push(colorMapping[value]); // Add the removed color back to the availableColors stack
                delete colorMapping[value];
                localStorage.setItem("colorMapping", JSON.stringify(colorMapping)); // Update colorMapping in localStorage
            }
        }

        const checkboxes = document.querySelectorAll(".form-check-input");

        function updateCheckboxColors() {
            checkboxes.forEach(function (checkbox) {
                if (checkbox.checked) {
                    const color = getColor(checkbox.value);
                    checkbox.classList.add("custom-checkbox");
                    checkbox.style.backgroundColor = color;
                    checkbox.style.borderColor = color;
                } else {
                    checkbox.classList.remove("custom-checkbox");
                    checkbox.style.backgroundColor = "";
                    checkbox.style.borderColor = "";
                }
            });
        }

        updateCheckboxColors();

        const facets = document.querySelectorAll('.ul-query.list');
        facets.forEach(elem => {
            const button = elem.querySelector('.li-search-toggle > .toggle-button')
            const hiddenItems = elem.querySelectorAll('.hidden-item');
            let isHidden = true;
            button.addEventListener('click', () => {
                button.textContent = isHidden ? 'Show less' : 'Show more';
                isHidden = !isHidden;
                hiddenItems.forEach(item => item.classList.toggle('hidden'));
            });
        });
    });