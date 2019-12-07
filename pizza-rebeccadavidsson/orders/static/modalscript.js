
$(document).ready(function(){

  $(".myModal").click(function(){

    var details = $(this).data("id").split(" ")

    // Get price from string (pizza, price)
    var price = details[1]
    var name = details[0]

    var div = document.getElementById('modalTitle');
    var title = name;
    div.innerHTML = title;

    // Insert price into div
    var price_div = document.getElementById("price_div");
    price_div.innerHTML = price;

    animateCSS(price_div, 'tada')
  });
});

function clearChecks() {
  console.log("Clearing checks");
  var allInputs = document.querySelectorAll(".form-check-input")
  for (i = 0; i < allInputs.length; i++) {
    allInputs[i].checked = false;
    allInputs[i].value = "unchecked";
  }
}

function animateCSS(element, animationName, callback) {
    const node = document.querySelector(".price_div");

    node.classList.add('animated', animationName)

    function handleAnimationEnd() {
        node.classList.remove('animated', animationName)
        node.removeEventListener('animationend', handleAnimationEnd)

        if (typeof callback === 'function') callback()
    }

    node.addEventListener('animationend', handleAnimationEnd)
}

// Change price after adding max 3 toppings
function checkTopping(elem) {

  // Change price of div
  var price_div = document.querySelector(".price_div");
  animateCSS(price_div, 'tada')

  // Check for max 3 toppings
  var allInputs = document.querySelectorAll(".form-check-input")
  counter = 0
  for (i = 0; i < allInputs.length; i++) {
    if (allInputs[i].value == "checked") {
      counter += 1
    }
  }
  if (counter == 3 && elem.checked == true) {
    alert("You can only select 3 toppings")
    elem.checked = false;
  }
  else {

    temp = parseFloat(price_div.innerHTML.toString())

    if (elem.value == "unchecked") {
      price = temp + 0.50
      price_div.innerHTML = price;
      elem.value = "checked";
    }
    else {
      price = temp - 0.50
      price_div.innerHTML = price;
      elem.value = "unchecked";
    }
  }
}

function addToppings() {

  // Get selected pizza
  var selected_pizza = document.getElementById("modalTitle").innerHTML

  // Collect all selected toppings
  var allInputs = document.querySelectorAll(".form-check-input")
  var toppingsArray = [selected_pizza]

  // Get current price
  var price_div = document.getElementById("price_div");
  price = price_div.innerHTML

  toppingsArray.push(price)

  for (i = 0; i < allInputs.length; i++) {
    if (allInputs[i].value == "checked") {
      toppingsArray.push(allInputs[i].name)
    }
  }


  // Convert to string to push to data for ajax request
  toppings = toppingsArray.join(",")

  // Send out new ajax request linked to add_topping() in views.py
  // data = string of item-name and topping id
  $.ajax({
       type: "GET",
       url: 'add_topping/',
       data: toppings,
       success:  function(response){
              
              console.log("Redirect to homepage");

              // Redirect to homepage
              window.location.href = "/"
          }
   });

}
