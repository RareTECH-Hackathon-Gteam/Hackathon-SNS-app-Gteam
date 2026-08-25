document.addEventListener("DOMContentLoaded", () => {
    const flashMessages = document.querySelectorAll(".flash-messages");

    flashMessages.forEach((flashMessage) => {
        setTimeout(() => {
            flashMessage.addEventListener(
                "transitionend",  
                () => {
                flashMessage.remove();
                },
                { once: true }
            );

            flashMessage.classList.add("flash-messages-hide");
        }, 3000);
    });
});