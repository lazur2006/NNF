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
function orderhistory_btn_action(route, basket_uid) {
  $.ajax({
    url: "/",
    data: JSON.stringify({ Route: route, basket_uid: basket_uid }),
    contentType: "application/json;charset=UTF-8",
    type: "POST",
    success: function (response) {
      $("#ordershistory_basket_" + basket_uid)
        .addClass("btn-success")
        .removeClass("btn-outline-dark");
      if (route == "ordershistory_delete") {
        location.reload();
      }

      console.log(response);
    },
    error: function (error) {
      console.log(error);
    },
  });
}
function create_recipe_cards() {
  $.ajax({
    url: "/",
    data: JSON.stringify({ Route: "create_cards" }),
    contentType: "application/json;charset=UTF-8",
    type: "POST",
    success: function (response) {
      console.log(response);
      var win = window.open("/cards", "_blank");
      if (win) {
        //Browser has allowed it to be opened
        win.focus();
      } else {
        //Browser has blocked it
        alert("Please allow popups for this website");
      }
    },
    error: function (error) {
      console.log(error);
    },
  });
}
function build_vendor_basket(response) {
  var vendor_ingredients = document.querySelector("#vendor_ingredients");
  var vendor_basket_total = document.querySelector("#baskets_total");
  var vendor_missing_ingredients_list = document.querySelector(
    "#vendor_missing_ingredients_list"
  );

  while (vendor_ingredients.children[1]) {
    vendor_ingredients.removeChild(vendor_ingredients.children[1]);
  }

  while (vendor_missing_ingredients_list.children[0]) {
    vendor_missing_ingredients_list.removeChild(
      vendor_missing_ingredients_list.children[0]
    );
  }

  $("#vendor_missing_ingredients").css({ display: "none" });
  $("#vendor_push_ingredients_success").css({ display: "none" });

  vendor_basket_total.textContent = response.total + " €";
  vendor_basket_total.disabled = true;

  $.each(response.vendorbasket, function (idx, element) {
    if (element.results.length != 0) {
      const li_vendor_ingredients = document.createElement("li");
      const div_vendor = document.createElement("div");
      const div_vendor_btn = document.createElement("div");
      const img = document.createElement("img");
      const div_btn_group = document.createElement("div");
      const btn_minus = document.createElement("button");
      const btn_cnt = document.createElement("button");
      const btn_add = document.createElement("button");
      const div_product = document.createElement("div");
      const span_needed = document.createElement("span");
      const div_name = document.createElement("div");
      const div_price = document.createElement("div");
      const div_amount = document.createElement("div");
      const div_skip = document.createElement("div");
      const i_prev = document.createElement("i");
      const i_next = document.createElement("i");

      search = element.search_amount + " " + element.search_term;
      image_uri = element.results[element.selected].image_uri;
      name = element.results[element.selected].name;
      price = element.results[element.selected].price + "€";
      product_id = element.results[element.selected].product_id;
      unit_quantity = element.results[element.selected].unit_quantity;
      amount = element.amount;

      img.setAttribute("src", image_uri);
      img.setAttribute(
        "style",
        "height:5em;width:auto;max-width:4.5em;object-fit:contain;"
      );
      if (amount == 0) {
        img.setAttribute(
          "style",
          "height:5em;width:auto;max-width:4.5em;object-fit:contain;filter: grayscale(1) opacity(0.5);"
        );
      }
      img.classList.add("m-3");

      //li_vendor_ingredients.textContent = search + " " + name + " " + price + " " + product_id + " " + unit_quantity;
      li_vendor_ingredients.classList.add("list-group-item");
      li_vendor_ingredients.classList.add("d-flex");
      li_vendor_ingredients.classList.add("align-items-center");

      div_vendor.classList.add("d-flex");
      div_vendor.classList.add("flex-column");
      div_vendor.classList.add("mt-4");
      div_vendor.classList.add("text-center");
      div_vendor.classList.add("align-items-center");
      div_vendor.appendChild(img);

      btn_minus.classList.add("btn");
      btn_minus.classList.add("btn-outline-dark");
      btn_minus.classList.add("btn-sm");
      btn_minus.setAttribute(
        "onclick",
        "vendor_change_ingredient('minus'," + idx + ")"
      );
      btn_minus.setAttribute("style", "width:2em");
      btn_minus.textContent = "-";

      btn_cnt.classList.add("btn");
      btn_cnt.classList.add("btn-outline-dark");
      btn_cnt.classList.add("btn-sm");
      btn_cnt.disabled = true;
      btn_cnt.textContent = amount;
      btn_cnt.setAttribute("style", "width:2.5em;");

      btn_add.classList.add("btn");
      btn_add.classList.add("btn-outline-dark");
      btn_add.classList.add("btn-sm");
      btn_add.setAttribute(
        "onclick",
        "vendor_change_ingredient('add'," + idx + ")"
      );
      btn_add.setAttribute("style", "width:2em");
      btn_add.textContent = "+";

      div_btn_group.classList.add("btn-group");
      div_btn_group.classList.add("m-3");
      div_btn_group.appendChild(btn_minus);
      div_btn_group.appendChild(btn_cnt);
      div_btn_group.appendChild(btn_add);

      span_needed.classList.add("badge");
      span_needed.classList.add("bg-dark");
      span_needed.classList.add("rounded-pill");
      span_needed.classList.add("text-wrap");
      span_needed.classList.add("text-break");
      span_needed.classList.add("mb-3");
      span_needed.textContent = search;

      div_name.classList.add("fw-bold");
      div_name.classList.add("text-wrap");
      div_name.classList.add("text-break");
      if (name.length > 60) {
        div_name.setAttribute("style", "font-size: 10pt;");
      } else {
        div_name.setAttribute("style", "font-size: 13pt;");
      }
      if (amount == 0) {
        div_name.classList.add("text-decoration-line-through");
      }

      div_name.textContent = name;

      div_price.classList.add("fw-lighter");
      div_price.classList.add("text-wrap");
      div_price.classList.add("fs-6");
      div_price.textContent = price;

      div_amount.classList.add("fw-lighter");
      div_amount.classList.add("text-wrap");
      div_amount.classList.add("fs-6");
      div_amount.textContent = unit_quantity;

      div_product.classList.add("d-flex");
      div_product.classList.add("flex-column");
      div_product.classList.add("justify-content-start");
      div_product.classList.add("align-items-start");
      div_product.classList.add("p-3");
      div_product.setAttribute("style", "width:100%;");
      div_product.appendChild(span_needed);
      div_product.appendChild(div_name);
      div_product.appendChild(div_price);
      div_product.appendChild(div_amount);

      div_skip.classList.add("d-flex");
      div_skip.classList.add("flex-column");
      div_skip.classList.add("justify-content-evenly");

      i_prev.classList.add("bi");
      i_prev.classList.add("bi-arrow-left-circle-fill");
      if (element.selected != 0) {
        i_prev.classList.add("text-dark");
      } else {
        i_prev.classList.add("text-light");
      }

      i_prev.classList.add("fs-3");
      i_prev.setAttribute(
        "onclick",
        "vendor_change_ingredient('prev'," + idx + ")"
      );

      i_next.classList.add("bi");
      i_next.classList.add("bi-arrow-right-circle-fill");
      if (element.selected < element.results.length - 1) {
        i_next.classList.add("text-dark");
      } else {
        i_next.classList.add("text-light");
      }

      i_next.classList.add("fs-3");
      i_next.setAttribute(
        "onclick",
        "vendor_change_ingredient('next'," + idx + ")"
      );

      div_skip.appendChild(i_prev);
      div_skip.appendChild(i_next);

      //div_vendor_btn.classList.add("mt-4");
      div_vendor.appendChild(div_btn_group);

      li_vendor_ingredients.appendChild(div_vendor);
      li_vendor_ingredients.appendChild(div_product);
      li_vendor_ingredients.appendChild(div_skip);

      vendor_ingredients.appendChild(li_vendor_ingredients);
    } else {
      //console.log(element.search_term)
    }
  });
  if (response.missing.length > 0) {
    $.each(response.missing, function (idx, element) {
      if (element != "Leitungswasser") {
        $("#vendor_missing_ingredients").css({ display: "inline-block" });
        const li_vendor_missing_ingredients_list = document.createElement("li");
        li_vendor_missing_ingredients_list.classList.add("list-group-item");
        li_vendor_missing_ingredients_list.classList.add("bg-transparent");
        li_vendor_missing_ingredients_list.classList.add("text-dark");
        li_vendor_missing_ingredients_list.classList.add("text-opacity-75");
        li_vendor_missing_ingredients_list.classList.add("fs-6");
        li_vendor_missing_ingredients_list.textContent = element;

        vendor_missing_ingredients_list.appendChild(
          li_vendor_missing_ingredients_list
        );
      }
    });
  }
}
function push_vendor_basket(vendor) {
  var spinner_push_vendor_basket = document.querySelector(
    "#spinner_push_vendor_basket"
  );
  var vendor_ingredients = document.querySelector("#vendor_ingredients");

  $("#spinner_push_vendor_basket").css({ display: "inline-block" });
  $("#check_push_vendor_basket").css({ display: "none" });

  $.ajax({
    url: "/",
    data: JSON.stringify({ vendor: vendor, Route: "push_vendor_basket" }),
    contentType: "application/json;charset=UTF-8",
    type: "POST",
    success: function (response) {
      console.log(response);
      $("#spinner_push_vendor_basket").css({ display: "none" });
      $("#check_push_vendor_basket").css({ display: "inline-block" });
      $("#push_vendor_basket").prop("disabled", true);

      while (vendor_ingredients.children[1]) {
        vendor_ingredients.removeChild(vendor_ingredients.children[1]);
      }

      if (response.missing.length < 2) {
        if (
          response.missing.length == 1 &&
          response.missing[0] == "Leitungswasser"
        ) {
          $("#vendor_push_ingredients_success").css({
            display: "inline-block",
          });
        } else if (response.missing.length == 0) {
          $("#vendor_push_ingredients_success").css({
            display: "inline-block",
          });
        }
      }

      create_recipe_cards();
    },
    error: function (error) {
      console.log(error);
    },
  });
}
function vendor_change_ingredient(f, idx) {
  console.log(f);
  console.log(idx);

  $.ajax({
    url: "/",
    data: JSON.stringify({ idx: idx, f: f, Route: "mod" }),
    contentType: "application/json;charset=UTF-8",
    type: "POST",
    success: function (response) {
      build_vendor_basket(response);
    },
    error: function (error) {
      console.log(error);
    },
  });
}
function checkout(vendor) {
  $("#spinner_" + vendor).css({ display: "inline-block" });
  $("#spinner_" + vendor + "_carticon").css({ display: "none" });
  $("#vendor_checkout_proceed_" + vendor).addClass("disabled");

  $.ajax({
    url: "/",
    data: JSON.stringify({ vendor: vendor, Route: "checkout" }),
    contentType: "application/json;charset=UTF-8",
    type: "POST",
    success: function (response) {
      console.log(response);
      $("#spinner_" + vendor + "_carticon").css({ display: "inline-block" });
      $("#spinner_" + vendor).css({ display: "none" });
      $("#vendor_checkout_proceed_" + vendor).removeClass("disabled");
      $("#push_vendor_basket").prop("disabled", false);

      build_vendor_basket(response);

      bootstrap.Offcanvas.getOrCreateInstance(
        $("#offcanvasRightCheckout")
      ).hide();
      bootstrap.Offcanvas.getOrCreateInstance(
        $("#offcanvasRightVendor")
      ).show();

      $("#offcanvasRightLabel").text(vendor);
      var push_vendor_basket = document.querySelector("#push_vendor_basket");
      var img_vendor_basket = document.querySelector("#img_vendor_basket");
      push_vendor_basket.setAttribute(
        "onclick",
        "push_vendor_basket('" + vendor + "')"
      );
      img_vendor_basket.setAttribute(
        "src",
        "/static/images/" + vendor + "_logo.svg"
      );

      //data-bs-target="#offcanvasRightLabelVendor"
    },
    error: function (error) {
      console.log(error);
    },
  });
}

function startConn(type) {
  $("#update_vendor_database").prop("disabled", true);
  var source = new EventSource("/progress?type=" + type + "");
  source.onmessage = function (event) {
    $(".progress-bar")
      .css("width", event.data + "%")
      .attr("aria-valuenow", event.data);
    $(".progress-bar-label").text(event.data + "%");

    if (event.data == 100 || event.data == "close") {
      source.close();
      $("#update_vendor_database").prop("disabled", false);
    }
  };
}

function deleteItem(item) {
  var node = document.getElementById("recipe_id_" + item);
  if (node.parentNode.childElementCount == 1) {
    clearBasket();
  } else {
    $.ajax({
      url: "/",
      data: JSON.stringify({ deleteItem: item, Route: "deleteItem" }),
      contentType: "application/json;charset=UTF-8",
      type: "POST",
      success: function (response) {
        //console.log(response);
        populateTable(response);
      },
      error: function (error) {
        //console.log(error);
      },
    });
  }
}

function populateTable(json) {
  var ingredientsTab = document.querySelector("#ingredients-tab");
  var recipesTab = document.querySelector("#recipes-tab");

  if ($("#ingredients-tab").children().length > 0) {
    while (ingredientsTab.firstChild) {
      ingredientsTab.removeChild(ingredientsTab.firstChild);
      recipesTab.removeChild(recipesTab.firstChild);
    }
  }

  const ul_ingredients = document.createElement("ul");
  const ul_recipes = document.createElement("ul");

  ul_ingredients.classList.add("list-group");
  ul_recipes.classList.add("list-group");

  if (typeof json["Amount"] != "undefined") {
    Object.keys(json["Name"]).forEach((row) => {
      const div_img = document.createElement("div");

      div_img.classList.add("ms-1");
      div_img.classList.add("mt-3");
      div_img.classList.add("mb-3");
      div_img.classList.add("me-3");
      div_img.classList.add("p-5");
      //div_img.classList.add('p-5');

      div_img.style.background = "url(" + json.img_uri[row] + ") scroll center";
      //"url('static/images/de-DE/" + json["ID"][row] + ".jpg') scroll center";
      div_img.style.height = "10vw";
      div_img.style.width = "10vw";
      div_img.style.maxHeight = "7em";
      div_img.style.maxWidth = "7em";
      div_img.style.borderRadius = "50%";
      div_img.style.backgroundPosition = "center";
      div_img.style.backgroundSize = "cover";

      const div_close = document.createElement("div");
      div_close.classList.add("position-absolute");
      div_close.classList.add("top-50");
      div_close.classList.add("start-100");
      div_close.classList.add("translate-middle");
      //div_close.classList.add('bg-warning');
      div_close.classList.add("rounded");

      const btn_close = document.createElement("div");
      //btn_close.setAttribute("id", row);
      btn_close.setAttribute("onclick", "deleteItem(" + json["ID"][row] + ")");

      btn_close.classList.add("btn");
      btn_close.classList.add("btn-outline-dark");
      btn_close.classList.add("btn-sm");
      btn_close.classList.add("rounded-circle");
      btn_close.style.verticalAlign = "middle";

      const i_close = document.createElement("div");
      i_close.classList.add("bi");
      i_close.classList.add("bi-x-circle-fill");

      btn_close.appendChild(i_close);
      div_close.appendChild(btn_close);

      const li_recipes = document.createElement("li");
      li_recipes.setAttribute("id", "recipe_id_" + json["ID"][row]);
      li_recipes.classList.add("list-group-item");
      li_recipes.classList.add("d-flex");
      li_recipes.classList.add("justify-content-left");
      li_recipes.classList.add("align-items-center");
      li_recipes.classList.add("text-break");
      li_recipes.classList.add("text-wrap");
      li_recipes.classList.add("pe-4");
      li_recipes.textContent = json["Name"][row];
      ul_recipes.appendChild(li_recipes);

      li_recipes.insertBefore(div_img, li_recipes.firstChild);
      li_recipes.appendChild(div_close);
      recipesTab.appendChild(ul_recipes);
    });

    Object.keys(json["Amount"]).forEach((row) => {
      const li_ingredients = document.createElement("li");
      li_ingredients.classList.add("list-group-item");
      li_ingredients.classList.add("d-flex");
      li_ingredients.classList.add("justify-content-between");
      li_ingredients.classList.add("align-items-center");
      li_ingredients.classList.add("text-break");
      li_ingredients.textContent = json["Ingredient"][row];
      ul_ingredients.appendChild(li_ingredients);

      const span_ingredients = document.createElement("span");
      span_ingredients.classList.add("badge");
      span_ingredients.classList.add("rounded-pill");
      span_ingredients.classList.add("text-bg-dark");
      span_ingredients.classList.add("m-3");
      if (json["Amount"][row] == 0) {
        span_ingredients.textContent = json["Unit"][row];
        if (
          json["Unit"][row] == "None" ||
          json["Unit"][row] == "Einheit" ||
          json["Unit"][row] == "nach Geschmack"
        ) {
          span_ingredients.textContent = "-";
        } else {
          span_ingredients.textContent = json["Unit"][row];
        }
      } else {
        span_ingredients.textContent =
          json["Amount"][row] + " " + json["Unit"][row];
        if (json["Amount"][row] == "None") {
          span_ingredients.textContent =
            json["Amount"][row] + " " + json["Ingredient"][row];
        }
      }

      li_ingredients.appendChild(span_ingredients);
      ingredientsTab.appendChild(ul_ingredients);
    });
  }
}

$(document).on("submit", "#index-form", function (e) {
  e.preventDefault();
  var selection = new Object();
  selection.Recipes = [];
  selection.Route = $("#btn").val();

  $("#loginspinner").css({ display: "inline-block" });
  $("#loginTryText").css({ display: "inline-block" });
  $("#loginSaveText").css({ display: "none" });
  $("#bichecklogin").css({ display: "none" });

  $($("#index-form").serializeArray()).each(function (i, field) {
    selection[field.name] = field.value;
  });

  $("input:checkbox[name=checkbox]:checked").each(function () {
    selection.Recipes.push($(this).val());
  });

  $.ajax({
    url: "/",
    data: JSON.stringify(selection),
    contentType: "application/json;charset=UTF-8",
    type: "POST",
    success: function (response) {
      //console.log(response);
      if (selection.Route == "saveCredentials") {
        var btn = document.getElementById("btn");
        var icon = document.getElementById("bichecklogin");
        $("#loginspinner").css({ display: "none" });
        $("#loginTryText").css({ display: "none" });
        $("#bichecklogin").css({ display: "inline-block" });
        if (response.status) {
          icon.classList.replace("bi-x", "bi-check-all");
          btn.classList.replace("btn-outline-dark", "btn-success");
          btn.classList.replace("btn-danger", "btn-success");
          $("#ToastObject").toast("show");
          var toastText = document.querySelector("#toastText");
          while (toastText.firstChild) {
            toastText.removeChild(toastText.firstChild);
          }
          $.each(response.info, function (k, v) {
            const list = document.createElement("li");
            const div_outer = document.createElement("div");
            const div_inner = document.createElement("div");

            list.classList.add("list-group-item");
            list.classList.add("d-flex");
            list.classList.add("justify-content-between");
            list.classList.add("align-items-start");

            div_outer.classList.add("ms-2");
            div_outer.classList.add("me-auto");
            div_outer.textContent = k;

            div_inner.classList.add("fw-bold");
            div_inner.textContent = v;

            div_outer.appendChild(div_inner);
            list.appendChild(div_outer);
            toastText.appendChild(list);
          });
        } else {
          icon.classList.replace("bi-check-all", "bi-x");
          btn.classList.replace("btn-outline-dark", "btn-danger");
          btn.classList.replace("btn-success", "btn-danger");
        }
        setCurrentUserStatus();
      } else {
        populateTable(response);
      }
    },
    error: function (error) {
      //console.log(error);
    },
  });
});

/*
    Is called if the clear basket button is called on the index page
*/
function clearBasket() {
  var ingredientsTab = document.querySelector("#ingredients-tab");
  var recipesTab = document.querySelector("#recipes-tab");
  $.ajax({
    url: "/",
    data: JSON.stringify({
      Route: "clearBasket",
    }),
    contentType: "application/json;charset=UTF-8",
    type: "POST",
    success: function (response) {
      if ($("#ingredients-tab").children().length > 0) {
        while (ingredientsTab.firstChild) {
          ingredientsTab.removeChild(ingredientsTab.firstChild);
          recipesTab.removeChild(recipesTab.firstChild);
        }
      }
      bootstrap.Offcanvas.getOrCreateInstance($("#offcanvasRight")).hide();
    },
    error: function (error) {
      //console.log(error);
    },
  });
}

/*
    Will be called if the vendor on Login page is changed - Dropdown menu
*/
function vendorChanged(vendor) {
  if (vendor.value == "REWE") {
    $("#ipaddress_div").css({ visibility: "visible" });
    $("#floatingIPaddress").prop("required", true);
  } else {
    $("#ipaddress_div").css({ visibility: "hidden" });
    $("#floatingIPaddress").prop("required", false);
  }
  var btn = document.getElementById("btn");
  btn.classList.replace("btn-success", "btn-outline-dark");
  btn.classList.replace("btn-danger", "btn-outline-dark");
  $("#loginspinner").css({ display: "none" });
  $("#loginTryText").css({ display: "none" });
  $("#bichecklogin").css({ display: "none" });
  $("#loginSaveText").css({ display: "inline-block" });
}

function setCurrentUserStatus() {
  var login_status_badge_REWE = document.getElementById(
    "login_status_badge_REWE"
  );
  var login_status_bi_REWE = document.getElementById("login_status_bi_REWE");
  var login_status_badge_Picnic = document.getElementById(
    "login_status_badge_Picnic"
  );
  var login_status_bi_Picnic = document.getElementById(
    "login_status_bi_Picnic"
  );
  var login_status_badge_HelloFresh = document.getElementById(
    "login_status_badge_HelloFresh"
  );
  var login_status_bi_HelloFresh = document.getElementById(
    "login_status_bi_HelloFresh"
  );
  var vendor_checkout_proceed_REWE = document.getElementById(
    "vendor_checkout_proceed_REWE"
  );
  var vendor_checkout_proceed_Picnic = document.getElementById(
    "vendor_checkout_proceed_Picnic"
  );

  //var btn_hellofresh_recent_week = document.querySelector('[name="btn_hellofresh_recent_week"]');

  $.ajax({
    url: "/",
    data: JSON.stringify({ Route: "getCurrentUserStatus" }),
    contentType: "application/json;charset=UTF-8",
    type: "POST",
    success: function (response) {
      if (response.REWE) {
        try {
          vendor_checkout_proceed_REWE.disabled = false;
        } catch (e) {}
        try {
          login_status_badge_REWE.classList.replace(
            "text-bg-secondary",
            "text-bg-success"
          );
        } catch (e) {}
        try {
          login_status_badge_REWE.setAttribute(
            "title",
            "Successfully logged in"
          );
        } catch (e) {}
        try {
          login_status_bi_REWE.classList.replace(
            "bi-exclamation-circle-fill",
            "bi-check-circle-fill"
          );
        } catch (e) {}
      } else {
        try {
          vendor_checkout_proceed_REWE.disabled = true;
        } catch (e) {}
        try {
          login_status_badge_REWE.classList.replace(
            "text-bg-success",
            "text-bg-secondary"
          );
        } catch (e) {}
        try {
          login_status_badge_REWE.setAttribute("title", "Not logged in");
        } catch (e) {}
        try {
          login_status_bi_REWE.classList.replace(
            "bi-check-circle-fill",
            "bi-exclamation-circle-fill"
          );
        } catch (e) {}
      }
      if (response.Picnic) {
        try {
          vendor_checkout_proceed_Picnic.disabled = false;
        } catch (e) {}
        try {
          login_status_badge_Picnic.classList.replace(
            "text-bg-secondary",
            "text-bg-success"
          );
        } catch (e) {}
        try {
          login_status_badge_Picnic.setAttribute(
            "title",
            "Successfully logged in"
          );
        } catch (e) {}
        try {
          login_status_bi_Picnic.classList.replace(
            "bi-exclamation-circle-fill",
            "bi-check-circle-fill"
          );
        } catch (e) {}
      } else {
        try {
          vendor_checkout_proceed_Picnic.disabled = true;
        } catch (e) {}
        try {
          login_status_badge_Picnic.classList.replace(
            "text-bg-success",
            "text-bg-secondary"
          );
        } catch (e) {}
        try {
          login_status_badge_Picnic.setAttribute("title", "Not logged in");
        } catch (e) {}
        try {
          login_status_bi_Picnic.classList.replace(
            "bi-check-circle-fill",
            "bi-exclamation-circle-fill"
          );
        } catch (e) {}
      }
      if (response.HelloFresh) {
        try {
          document.querySelector(
            '[name="btn_hellofresh_recent_week"]'
          ).disabled = false;
        } catch (e) {}
        try {
          login_status_badge_HelloFresh.classList.replace(
            "text-bg-secondary",
            "text-bg-success"
          );
        } catch (e) {}
        try {
          login_status_badge_HelloFresh.setAttribute(
            "title",
            "Successfully logged in"
          );
        } catch (e) {}
        try {
          login_status_bi_HelloFresh.classList.replace(
            "bi-exclamation-circle-fill",
            "bi-check-circle-fill"
          );
        } catch (e) {}
      } else {
        try {
          document.querySelector(
            '[name="btn_hellofresh_recent_week"]'
          ).disabled = true;
        } catch (e) {}
        try {
          login_status_badge_HelloFresh.classList.replace(
            "text-bg-success",
            "text-bg-secondary"
          );
        } catch (e) {}
        try {
          login_status_badge_HelloFresh.setAttribute("title", "Not logged in");
        } catch (e) {}
        try {
          login_status_bi_HelloFresh.classList.replace(
            "bi-check-circle-fill",
            "bi-exclamation-circle-fill"
          );
        } catch (e) {}
      }
    },
    error: function (error) {
      //console.log(error);
    },
  });
}

/*
    Is called when the page is loaded completly
*/
$(document).ready(function () {
  /*| Setup the IP input mask for Login page |*/
  var ipv4_address = $("#floatingIPaddress");
  ipv4_address.inputmask({
    alias: "ip",
    greedy: false,
  });

  /*| Start progress connection for Update page |*/
  startConn("retrieve");

  setCurrentUserStatus();

  /*| Setup tooltips in general |*/
  var tooltipList = [
    ...document.querySelectorAll('[data-bs-toggle="tooltip"]'),
  ].map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl));
});
