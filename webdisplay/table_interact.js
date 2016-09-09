function create_button (name, parentID, onclick_function) {
    var parentElement = document.getElementById(parentID);
    var button = document.createElement("button");
    button.textContent = name;
    button.addEventListener("click", onclick_function);
    parentElement.appendChild(button)
};

function create_checkbox (name, parentID) {
    var parentElement = document.getElementById(parentID);
    var parElement = document.createElement("p");
    var checkbox = document.createElement("input");
    var nameText = document.createTextNode(name);
    checkbox.type = "checkbox";
    checkbox.id = name;
    //checkbox.value = name;
    //<input class="messageCheckbox" type="checkbox" value="3" name="mailId[]">
    //<input type="checkbox" name="vehicle" value="Bike">
    //checkbox.textContent = name;
    //parElement.textContent = name;
    parElement.appendChild(checkbox);
    parElement.appendChild(nameText);
    parentElement.appendChild(parElement)
};

function testlog() {
    console.log("testing")
};

function expand_plotcontrol (divID, json_location) {
    reset_element(divID);
    loadJSON(function (jsonString) {
        var jsonObject = JSON.parse(jsonString);
        var name_array = [];
        //plotTitles([create_checkbox, function (x) {name_array.push(x)}], jsonObject[0], null, divID);
        plotTitles(create_checkbox, jsonObject[0], null, divID);
        //create_button("Hide", divID, function () {console.log("click"); console.log(name_array)})
        create_button("Hide", divID, function () {loadJSON(rebuild_table_function(table_info, [0, 2]), json_location)})
    }, json_location)
}

//function checkbox_checker (

function expand_plotcontrol_old_2 (divID, json_location) {
    return function () {
        console.log("test");
        reset_element(divID);
        loadJSON(function (jsonString) {
            var jsonObject = JSON.parse(jsonString);
            //plotTitles(create_button, jsonObject[0], null, divID, testlog)
            plotTitles(create_checkbox, jsonObject[0], null, divID)
        }, json_location)
    }
}

function expand_plotcontrol_old (divID) {
    return function () {
        reset_element(divID);
        create_button("subtest1", divID, testlog);
        create_button("subtest2", divID, testlog);
        create_button("subtest3", divID, testlog);
    }
}

 //<button style="position: fixed; bottom:15px;right:5px;" onclick="loadJSON(rebuild_table_function(table_info, [0, 2]), json_location)">Test</button>
