function openDeleteConfirm(button) {
  const postCard = button.closest(".post-card");
  const confirmArea = postCard.querySelector(".delete-confirm");

  confirmArea.classList.add("is-open");
}

function closeDeleteConfirm(button) {
  const confirmArea = button.closest(".delete-confirm");

  confirmArea.classList.remove("is-open");
}