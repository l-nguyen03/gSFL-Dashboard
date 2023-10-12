const selectBtn1 = document.querySelector(".select-btn1");
const dts = document.querySelectorAll(".dt");
const selectedItemsContainer = document.querySelector(".selected-items");
const dropdownList = document.querySelector(".list-dts");

selectBtn1.addEventListener("click", () => {
  selectBtn1.classList.toggle("open");
  if (selectBtn1.classList.contains("open")) { // List is being opened
      // Hide selected items
      selectedItemsContainer.style.display = "none";
  } else { // List is being closed
      // Show selected items
      selectedItemsContainer.style.display = "block";
}
});

dts.forEach((dt) => {
  dt.addEventListener("click", () => {
    dt.classList.toggle("checked");

    let checked1 = document.querySelectorAll(".dt.checked"),
      btnText1 = document.querySelector(".btn-text1");

    if (checked1 && checked1.length == 1) {
      btnText1.innerText = `${checked1.length} DT Selected`;
    } else if (checked1 && checked1.length > 1) {
      btnText1.innerText = `${checked1.length} DTs Selected`;
    } else {
      btnText1.innerText = "Select DTs";
    }
     // Fetch currently selected DTs from the hidden input
        const selectedDTsInputs = document.querySelectorAll("input[name='selectedDTs']");
        let currentDTs = [];
        if (selectedDTsInputs[0].value) {
            currentDTs = JSON.parse(selectedDTsInputs[0].value);
        }

        const dtValue = {
            name: dt.querySelector(".dt-text").textContent,
            id: dt.getAttribute("data-prop-id")
        };

        if (dt.classList.contains("checked")) {
            // Add the selected DT to the current DTs
            currentDTs.push(dtValue);
        } else {
            // Remove the unselected DT from the current DTs
            currentDTs = currentDTs.filter(item => item.id !== dtValue.id);
        }

        // Update the hidden input value with the modified DTs
        selectedDTsInputs.forEach(input => {
            input.value = JSON.stringify(currentDTs);
        });

        // Update the display of selected items
        selectedItemsContainer.innerHTML = ""; // clear previous selections
        currentDTs.forEach(item => {
            const selectedItem = document.createElement("div");
            selectedItem.textContent = item.name;
            selectedItemsContainer.appendChild(selectedItem);
        });

        updateCreateButtonState();
  });
});


function updateCreateButtonState() {
  const selectedDTs = document.querySelectorAll(".dt.checked");
  const createButtons = document.querySelectorAll(".btn_create");

  createButtons.forEach(button => {
    button.disabled = selectedDTs.length > 0 ? false : true;
  });
}

// function showAvailableData() {
//   var boxContainer = document.querySelector('.box-container');
//   var boxes = boxContainer.querySelectorAll('.box');
  
//   // Get selected digital twins
//   var selectedDTs = document.querySelector("input[name='selectedDT']").value.split(",");

//   // Iterate through each box and display only those that match the selected digital twins prefix
//   boxes.forEach(function(box) {
//     var boxName = box.getAttribute('data-dt-name');
    
//     // Check if the boxName starts with any of the prefixes in the selectedDTs array
//     var hasMatchingPrefix = selectedDTs.some(dt => boxName.startsWith(dt));

//     if (hasMatchingPrefix) {
//         box.style.display = 'block';
//     } else {
//         box.style.display = 'none';
//     }
//   });
//   boxContainer.style.display = 'block';
// }

