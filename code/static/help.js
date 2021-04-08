"use strict";
/////////////////////////
// comments

/////////////////////////
// variables
const alertCloseBtn = document.querySelectorAll(".close-btn");
const alertMessageDiv = document.querySelectorAll(".flash-message");

/////////////////////////

// functions

const alertClose = function () {
  alertMessageDiv.forEach((div) => {
    div.style.display = "none";
  });
};

/////////////////////////

// event listeners
alertCloseBtn.forEach((btn) => {
  btn.addEventListener("click", alertClose);
});
