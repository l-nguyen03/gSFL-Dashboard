const selectBtn1 = document.querySelector(".select-btn1");
const assets = document.querySelectorAll(".asset");

selectBtn1.addEventListener("click", () => {
  selectBtn1.classList.toggle("open");

  if (selectBtn1.classList.contains("open")) {
    selectBtn2.classList.remove("open");
    selectBtn3.classList.remove("open"); // Close the other section
  }
});

assets.forEach((asset) => {
  asset.addEventListener("click", () => {

    const wasChecked = asset.classList.contains("checked");

    if (!wasChecked) {
      // If asset was not checked, uncheck all other assets
      assets.forEach(otherAsset => {
        if (otherAsset !== asset) {
          otherAsset.classList.remove("checked");
        }
      });

      // Toggle the clicked asset's checked state
      asset.classList.toggle("checked");
    }

    // Check how many assets are now selected (should be 0 or 1)
    let checked1 = document.querySelectorAll(".asset.checked"),
        btnText1 = document.querySelector(".btn-text1");

    if (checked1.length === 1) {
      btnText1.innerText = "1 Asset Selected";
    } else {
      btnText1.innerText = "Select Asset";
    }

    // Update the hidden input value with selected asset
    const selectedAssets = Array.from(document.querySelectorAll(".asset.checked"))
      .map(asset => asset.dataset.propId)
      .join(",");
    document.querySelector("input[name='selectedAssets']").value = selectedAssets;

      updateCreateButtonState();

    /// Close the dropdown
    selectBtn1.classList.remove("open");
});
});



const selectBtn2 = document.querySelector(".select-btn2");
const policies2 = document.querySelectorAll(".policy2");

selectBtn2.addEventListener("click", () => {
  selectBtn2.classList.toggle("open");

  if (selectBtn2.classList.contains("open")) {
    selectBtn1.classList.remove("open");
    selectBtn3.classList.remove("open"); // Close the other section
  }
});

policies2.forEach((policy) => {
  policy.addEventListener("click", () => {
    const checkedPolicies2 = document.querySelectorAll(".policy2.checked");
    const btnText2 = document.querySelector(".btn-text2");

    // Uncheck previously checked items
    checkedPolicies2.forEach((checkedPolicy) => {
      if (checkedPolicy !== policy) {
        checkedPolicy.classList.remove("checked");
      }
    });
    const wasChecked = policy.classList.contains("checked");
    // Toggle the current item's checked state
    policy.classList.toggle("checked");

    const checked2 = document.querySelectorAll(".policy2.checked");

    if (checked2.length === 1) {
      btnText2.innerText = `${checked2.length} Policy Selected`;
    } else {
      btnText2.innerText = "Select Access Policy";
    }

    // Update the hidden input value with selected policy
    const selectedPolicy = Array.from(document.querySelectorAll(".policy2.checked"))
      .map(policy => policy.querySelector(".policy-text").textContent)
      .join(",");
    document.querySelector("input[name='selectedAccessPolicy']").value = selectedPolicy;

    updateCreateButtonState();
    if (!wasChecked) {
      selectBtn2.classList.remove("open");
    }
  });
});

const selectBtn3 = document.querySelector(".select-btn3");
const policies3 = document.querySelectorAll(".policy3");

selectBtn3.addEventListener("click", () => {
  selectBtn3.classList.toggle("open");

  if (selectBtn3.classList.contains("open")) {
    selectBtn1.classList.remove("open");
    selectBtn2.classList.remove("open"); // Close the other section
  }
});

policies3.forEach((policy) => {
  policy.addEventListener("click", () => {
    const checkedPolicies3 = document.querySelectorAll(".policy3.checked");
    const btnText3 = document.querySelector(".btn-text3");

    // Uncheck previously checked items
    checkedPolicies3.forEach((checkedPolicy) => {
      if (checkedPolicy !== policy) {
        checkedPolicy.classList.remove("checked");
      }
    });

    const wasChecked = policy.classList.contains("checked");
    // Toggle the current item's checked state
    policy.classList.toggle("checked");

    const checked3 = document.querySelectorAll(".policy3.checked");

    if (checked3.length === 1) {
      btnText3.innerText = `${checked3.length} Policy Selected`;
    } else {
      btnText3.innerText = "Select Contract Policy";
    }

    // Update the hidden input value with selected policy
    const selectedPolicy = Array.from(document.querySelectorAll(".policy3.checked"))
      .map(policy => policy.querySelector(".policy-text").textContent)
      .join(",");
    document.querySelector("input[name='selectedContractPolicy']").value = selectedPolicy;

    updateCreateButtonState();
    if (!wasChecked) {
      selectBtn3.classList.remove("open");
    }
  });
});

function updateCreateButtonState() {
  const selectedAssets = document.querySelectorAll(".asset.checked");
  const selectedAccessPolicies = document.querySelectorAll(".policy2.checked");
  const selectedContractPolicies = document.querySelectorAll(".policy3.checked");
  const contractIDValue = document.querySelector("#visibleContractID").value.trim();
  const createButton = document.querySelector(".btn_create");

  const durationInput = document.querySelector("#durationInput");
  const hiddenDurationInput = document.querySelector("#duration");

  hiddenDurationInput.value = durationInput.value.trim();


  const hiddenContractIDField = document.querySelector("#contractID");
  hiddenContractIDField.value = contractIDValue;
  
  if (selectedAssets.length > 0 && selectedAccessPolicies.length > 0 && selectedContractPolicies.length > 0 && contractIDValue) {
    createButton.disabled = false;
  } else {
    createButton.disabled = true;
  }
}