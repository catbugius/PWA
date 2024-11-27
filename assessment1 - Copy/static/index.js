// Event listener for the 'click' event on the document
document.addEventListener("click", e => {
    // Check if the clicked element has the data-dropdown-button attribute
    const isDropdownButton = e.target.matches("[data-dropdown-button]")

    // If the clicked element is inside an active dropdown, we don't want to do anything
    if (!isDropdownButton && e.target.closest('[data-dropdown]') != null) return

    let currentDropdown
    // If the clicked element is a dropdown button, find its closest dropdown element
    if (isDropdownButton) {
        currentDropdown = e.target.closest('[data-dropdown]')
        // Toggle the 'active' class on the current dropdown to show or hide it
        currentDropdown.classList.toggle('active')
    }

    // For all other dropdowns that are active, remove the 'active' class unless it's the current one
    document.querySelectorAll("[data-dropdown].active").forEach(dropdown => {
        // If the dropdown is the current one, skip removing the 'active' class
        if (dropdown === currentDropdown) return
        // Remove 'active' class from all other dropdowns
        dropdown.classList.remove('active')
    })
})
