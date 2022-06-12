// $(function() {
//   var availableTags = [
//     {%for tags in tags %}
//     "{{tags}}",
//     {% endfor %}
//   ];
//   $("#tags").autocomplete({
//     source: function(request, response) {
//       var results = $.ui.autocomplete.filter(availableTags, request.term);
//       response(results.slice(0, 10));
//     }
//   });
// });
function checkout(vendor){
  $('#spinner_picnic').css({"display":"inline-block"});
  $('#spinner_picnic_carticon').css({"display":"none"});
  $('.btn').addClass('disabled')

  $.ajax({
    url: '/',
    data: JSON.stringify({vendor: vendor,Route: "checkout"}),
    contentType: 'application/json;charset=UTF-8',
    type: 'POST',
    success: function(response) {
      console.log(response);
      $('#spinner_picnic_carticon').css({"display":"inline-block"});
      $('#spinner_picnic').css({"display":"none"});
      $('.btn').removeClass('disabled')
      //populateTable(response);
    },
    error: function(error) {
      console.log(error);
    }
  })
}

function startConn(type) {
  $('.btn').prop('disabled', true);
  var source = new EventSource("/progress?type="+ type +"");
  source.onmessage = function(event) {
    $('.progress-bar').css('width', event.data + '%').attr('aria-valuenow', event.data);
    $('.progress-bar-label').text(event.data + '%');

    if (event.data == 100 || event.data == "close") {
      source.close()
      $('.btn').prop('disabled', false);
    }
  }
}

function deleteItem(item) {

  var node = document.getElementById("recipe_id_" + item);
  if (node.parentNode.childElementCount == 1) {
    clearBasket();
  }
  else{
    $.ajax({
      url: '/',
      data: JSON.stringify({deleteItem: item,Route: "deleteItem"}),
      contentType: 'application/json;charset=UTF-8',
      type: 'POST',
      success: function(response) {
        //console.log(response);
        populateTable(response);
      },
      error: function(error) {
        //console.log(error);
      }
    })
  }
}

function populateTable(json) {
  var ingredientsTab = document.querySelector("#ingredients-tab");
  var recipesTab = document.querySelector("#recipes-tab");

  if ($('#ingredients-tab').children().length > 0) {
    while (ingredientsTab.firstChild) {
      ingredientsTab.removeChild(ingredientsTab.firstChild);
      recipesTab.removeChild(recipesTab.firstChild);
    }
  }

  const ul_ingredients = document.createElement("ul");
  const ul_recipes = document.createElement("ul");

  ul_ingredients.classList.add('list-group');
  ul_recipes.classList.add('list-group');

  if (typeof json['Amount'] != 'undefined') {

    Object.keys(json['Name']).forEach((row) => {
      const div_img = document.createElement("div");

      div_img.classList.add('ms-1');
      div_img.classList.add('mt-3');
      div_img.classList.add('mb-3');
      div_img.classList.add('me-3');
      div_img.classList.add('p-5');
      //div_img.classList.add('p-5');

      div_img.style.background = "url('static/images/de-DE/" + json['ID'][row] + ".jpg') scroll center";
      div_img.style.height = "10vw";
      div_img.style.width = "10vw";
      div_img.style.maxHeight = "7em";
      div_img.style.maxWidth = "7em";
      div_img.style.borderRadius = "50%";
      div_img.style.backgroundPosition = "center";
      div_img.style.backgroundSize = "cover";

      const div_close = document.createElement("div");
      div_close.classList.add('position-absolute');
      div_close.classList.add('top-50');
      div_close.classList.add('start-100');
      div_close.classList.add('translate-middle');
      //div_close.classList.add('bg-warning');
      div_close.classList.add('rounded');

      const btn_close = document.createElement("div");
      //btn_close.setAttribute("id", row);
      btn_close.setAttribute("onclick", "deleteItem(" + json['ID'][row] + ")");

      btn_close.classList.add('btn');
      btn_close.classList.add('btn-outline-dark');
      btn_close.classList.add('btn-sm');
      btn_close.classList.add('rounded-circle');
      btn_close.style.verticalAlign = "middle";

      const i_close = document.createElement("div");
      i_close.classList.add('bi');
      i_close.classList.add('bi-x-circle-fill');

      btn_close.appendChild(i_close);
      div_close.appendChild(btn_close);


      const li_recipes = document.createElement("li");
      li_recipes.setAttribute("id", "recipe_id_" + json['ID'][row]);
      li_recipes.classList.add('list-group-item');
      li_recipes.classList.add('d-flex');
      li_recipes.classList.add('justify-content-left');
      li_recipes.classList.add('align-items-center');
      li_recipes.classList.add('text-break');
      li_recipes.classList.add('text-wrap');
      li_recipes.classList.add('pe-4');
      li_recipes.textContent = json['Name'][row];
      ul_recipes.appendChild(li_recipes);

      li_recipes.insertBefore(div_img, li_recipes.firstChild);
      li_recipes.appendChild(div_close);
      recipesTab.appendChild(ul_recipes);
    })

    Object.keys(json['Amount']).forEach((row) => {
      const li_ingredients = document.createElement("li");
      li_ingredients.classList.add('list-group-item');
      li_ingredients.classList.add('d-flex');
      li_ingredients.classList.add('justify-content-between');
      li_ingredients.classList.add('align-items-center');
      li_ingredients.classList.add('text-break');
      li_ingredients.textContent = json['Ingredient'][row];
      ul_ingredients.appendChild(li_ingredients);

      const span_ingredients = document.createElement("span");
      span_ingredients.classList.add('badge');
      span_ingredients.classList.add('rounded-pill');
      span_ingredients.classList.add('text-bg-dark');
      span_ingredients.classList.add('m-3');
      if (json['Amount'][row] == 0) {
        span_ingredients.textContent = json['Unit'][row];
        if (json['Unit'][row] == 'None' || json['Unit'][row] == 'Einheit' || json['Unit'][row] == 'nach Geschmack') {
          span_ingredients.textContent = '-';
        } else {
          span_ingredients.textContent = json['Unit'][row];
        }
      } else {
        span_ingredients.textContent = json['Amount'][row] + " " + json['Unit'][row];
        if (json['Amount'][row] == 'None') {
          span_ingredients.textContent = json['Amount'][row] + " " + json['Ingredient'][row];
        }
      }

      li_ingredients.appendChild(span_ingredients);
      ingredientsTab.appendChild(ul_ingredients);
    })
  }
}

$(document).on('submit', '#index-form', function(e) {
  e.preventDefault();
  var selection = new Object();
  selection.Recipes = [];
  selection.Route = $("#btn").val();

  $('#loginspinner').css({"display":"inline-block"});
  $('#loginTryText').css({"display":"inline-block"});
  $('#loginSaveText').css({"display":"none"});
  $('#bichecklogin').css({"display":"none"});

  $($('#index-form').serializeArray()).each(function(i, field){
    selection[field.name] = field.value;
  });

  $("input:checkbox[name=checkbox]:checked").each(function() {
    selection.Recipes.push($(this).val());
  });

  $.ajax({
    url: '/',
    data: JSON.stringify(selection),
    contentType: 'application/json;charset=UTF-8',
    type: 'POST',
    success: function(response) {
      //console.log(response);
      if(selection.Route == "saveCredentials"){
        var btn = document.getElementById("btn")
        var icon = document.getElementById("bichecklogin")
        $('#loginspinner').css({"display":"none"});
        $('#loginTryText').css({"display":"none"});
        $('#bichecklogin').css({"display":"inline-block"});
        if(response.status){
          icon.classList.replace("bi-x", "bi-check-all");
          btn.classList.replace("btn-outline-dark", "btn-success");
          btn.classList.replace("btn-danger", "btn-success");
          $("#ToastObject").toast("show");
          var toastText = document.querySelector("#toastText");
          while (toastText.firstChild) {
            toastText.removeChild(toastText.firstChild);
          }
          $.each(response.info, function(k,v) {
              const list = document.createElement("li");
              const div_outer = document.createElement("div");
              const div_inner = document.createElement("div");

              list.classList.add('list-group-item');
              list.classList.add('d-flex');
              list.classList.add('justify-content-between');
              list.classList.add('align-items-start');

              div_outer.classList.add('ms-2')
              div_outer.classList.add('me-auto')
              div_outer.textContent = k;

              div_inner.classList.add('fw-bold')
              div_inner.textContent = v;

              div_outer.appendChild(div_inner);
              list.appendChild(div_outer);
              toastText.appendChild(list);
          });
        }
        else {
          icon.classList.replace("bi-check-all", "bi-x");
          btn.classList.replace("btn-outline-dark", "btn-danger");
          btn.classList.replace("btn-success", "btn-danger");
        }

      }
      else{
        populateTable(response);
      }

    },
    error: function(error) {
      //console.log(error);
    }
  })
});

/*
    Is called if the clear basket button is called on the index page
*/
function clearBasket() {
  var ingredientsTab = document.querySelector("#ingredients-tab");
  var recipesTab = document.querySelector("#recipes-tab");
  $.ajax({
    url: '/',
    data: JSON.stringify({
      Route: "clearBasket"
    }),
    contentType: 'application/json;charset=UTF-8',
    type: 'POST',
    success: function(response) {
      if ($('#ingredients-tab').children().length > 0) {
        while (ingredientsTab.firstChild) {
          ingredientsTab.removeChild(ingredientsTab.firstChild);
          recipesTab.removeChild(recipesTab.firstChild);
        }
      }
      bootstrap.Offcanvas.getOrCreateInstance($('#offcanvasRight')).hide()
    },
    error: function(error) {
      //console.log(error);
    }
  })
};

/*
    Is called when the page is loaded completly
*/
$(document).ready(function() {
   /*| Setup the IP input mask for Login page |*/
  var ipv4_address = $('#floatingIPaddress');
  ipv4_address.inputmask({
      alias: "ip",
      greedy: false
  });

  /*| Start progress connection for Update page |*/
  startConn("retrieve");

  /*| Setup tooltips in general |*/
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
});

/*
    Will be called if the vendor on Login page is changed - Dropdown menu
*/
function vendorChanged(vendor){
  if(vendor.value == "REWE"){
    $('#ipaddress_div').css({"visibility":"visible"});
    $("#floatingIPaddress").prop('required',true);
  }
  else{
    $('#ipaddress_div').css({"visibility":"hidden"});
    $("#floatingIPaddress").prop('required',false);
  }
  var btn = document.getElementById("btn")
  btn.classList.replace("btn-success", "btn-outline-dark");
  btn.classList.replace("btn-danger", "btn-outline-dark");
  $('#loginspinner').css({"display":"none"});
  $('#loginTryText').css({"display":"none"});
  $('#bichecklogin').css({"display":"none"});
  $('#loginSaveText').css({"display":"inline-block"});
}
