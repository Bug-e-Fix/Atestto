document.addEventListener("DOMContentLoaded", () => {
    const tabs = document.querySelectorAll(".tab");
    const contents = document.querySelectorAll(".tab-content");

    tabs.forEach((tab, index) => {
        tab.addEventListener("click", () => {
            // Remove active de todos
            tabs.forEach(t => t.classList.remove("active"));
            contents.forEach(c => c.classList.remove("active"));

            // Adiciona active ao clicado
            tab.classList.add("active");
            contents[index].classList.add("active");
        });
    });

    // Ativa a primeira aba por padrão
    if (tabs.length > 0) {
        tabs[0].classList.add("active");
        contents[0].classList.add("active");
    }
});
