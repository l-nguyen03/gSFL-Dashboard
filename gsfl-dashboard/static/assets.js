const selectBtn1 = document.querySelector(".select-btn1");
const assets = document.querySelectorAll(".asset");

selectBtn1.addEventListener("click", () => {
  selectBtn1.classList.toggle("open");
});

assets.forEach((asset) => {
  asset.addEventListener("click", () => {
    asset.classList.toggle("checked");

    let checked1 = document.querySelectorAll(".asset.checked"),
      btnText1 = document.querySelector(".btn-text1");

    if (checked1 && checked1.length == 1) {
      btnText1.innerText = `${checked1.length} Asset Selected`;
    } else if (checked1 && checked1.length > 1) {
      btnText1.innerText = `${checked1.length} Assets Selected`;
    } else {
      btnText1.innerText = "Select Assets";
    }

    // Update the hidden input value with selected assets
    const selectedAssets = Array.from(document.querySelectorAll(".asset.checked"))
      .map(asset => asset.querySelector(".asset-text").textContent)
      .join(",");

    document.querySelector("input[name='selectedAssets']").value = selectedAssets;

    updateCreateButtonState();
  });
});


function updateCreateButtonState() {
  const selectedAssets = document.querySelectorAll(".asset.checked");
  const nameInput = document.getElementById("nameInput");
  const contentInput = document.getElementById("contentInput");
  const createButton = document.querySelector(".btn_create");

  // Update the hidden input values
  document.getElementById("assetNameInput").value = nameInput.value.trim();
  document.getElementById("assetContentInput").value = contentInput.value.trim();


  if (selectedAssets.length > 0 && nameInput.value.trim() !== "" && contentInput.value.trim() !== "") {
    createButton.disabled = false;
  } else {
    createButton.disabled = true;
  }
}