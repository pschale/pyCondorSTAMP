var start_index_global = 0;
var numplots_global = 25;
var tablelength = null;

function create_button (name, parentID, onclick_function, titlename = null) {
    var parentElement = document.getElementById(parentID);
    var button = document.createElement("button");
    button.textContent = name;
    button.addEventListener("click", onclick_function);
    if (titlename) {
        button.title = titlename
    };
    parentElement.appendChild(button)
};

function create_checkbox (name, parentID) {
    var parentElement = document.getElementById(parentID);
    var parElement = document.createElement("p");
    var checkbox = document.createElement("input");
    var nameText = document.createTextNode(name);
    checkbox.type = "checkbox";
    checkbox.id = name;
    checkbox.checked = true;
    parElement.appendChild(checkbox);
    parElement.appendChild(nameText);
    parentElement.appendChild(parElement)
};

function hide_plotcontrol (divID, json_location) {
    reset_element(divID);
    set_class(divID, "plotminimized");
    create_button("Plot control", divID, function () {expand_plotcontrol(divID, json_location)}, "Open plot controls")
};

function set_class (elementID, classname) {
    document.getElementById(elementID).className = classname
};

function create_textinput(parentID, elementID, global_var) {
    var parentElement = document.getElementById(parentID);
    var textbox = document.createElement("input");
    textbox.type = "text";
    textbox.size = "2";
    textbox.value = global_var;
    textbox.id = elementID;
    textbox.title = elementID;
    parentElement.appendChild(textbox)
};

function settablelength (jsonString) {
    jsonObject = JSON.parse(jsonString);
    tablelength = jsonObject["plot_info"].length;
};

function prevplots (json_location) {
    numplots_global = parseInt(document.getElementById("Number plot rows").value);
    if (start_index_global - numplots_global < 0) {
        start_index_global = 0
    } else {
        start_index_global -= numplots_global;
    }
    document.getElementById("Start plot row").value = start_index_global+1;
    loadJSON(build_table_function(table_info, check_checkboxes(jsonObject), start_index_global, numplots_global), json_location)
};

function nextplots (json_location) {
    if (start_index_global + numplots_global < tablelength) {
        start_index_global += numplots_global;
        numplots_global = parseInt(document.getElementById("Number plot rows").value);
        document.getElementById("Start plot row").value = start_index_global+1;
        loadJSON(build_table_function(table_info, check_checkboxes(jsonObject), start_index_global, numplots_global), json_location)
    } else {
        var plotnum = start_index_global + numplots_global;
        alert("Warning: Attempted to start viewing at plot number " + plotnum.toString() + ". Only " + tablelength.toString() + " viewable plots.")
    }
};

function updaterowinfo () {
    start_index_temp = parseInt(document.getElementById("Start plot row").value)-1;
    numplots_global = parseInt(document.getElementById("Number plot rows").value);
    if (start_index_temp < 0) {
        start_index_global = 0
        plotnum = start_index_global + 1;
        document.getElementById("Start plot row").value = plotnum.toString();
    } else if (start_index_temp < tablelength) {
        start_index_global = start_index_temp;
    } else {
        plotnum = start_index_temp + 1;
        alert("Warning: Attempted to start viewing at plot number " + plotnum.toString() + ". Only " + tablelength.toString() + " viewable plots.")
    }
};

function expand_plotcontrol (divID, json_location) {
    reset_element(divID);
    set_class(divID, "plotcontrol");
    loadJSON(function (jsonString) {
        var jsonObject = JSON.parse(jsonString);
        var name_array = [];
        create_button("<<", divID, function () {prevplots(json_location)}, "Previous plots");
        create_textinput(divID, "Start plot row", start_index_global+1);
        create_textinput(divID, "Number plot rows", numplots_global);
        create_button(">>", divID, function () {nextplots(json_location)}, "Next plots");
        plotTitles(create_checkbox, jsonObject, null, divID);
        create_button("Update", divID, function () {updaterowinfo(); loadJSON(build_table_function(table_info, check_checkboxes(jsonObject), start_index_global, numplots_global), json_location)}, "Update displayed plots");
        create_button("Hide", divID, function () {hide_plotcontrol(divID, json_location)}, "Hide plot controls")
    }, json_location)
};

function checkbox_checker (checkbox_id, check_array) {
    var checkbox = document.getElementById(checkbox_id);
    if (checkbox.checked) {
        check_array.push(1)
    } else {
        check_array. push(0)
    }
};

function check_checkboxes (list_item) {
    var checks = [];
    plotTitles(checkbox_checker, list_item, null, checks);
    var indices = [];
    for (i = 0; i < checks.length; i++) {
        if (checks[i]) {
            indices.push(i)
        }
    };
    return indices
}
