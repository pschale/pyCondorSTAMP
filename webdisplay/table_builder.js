function build_info_cell (cell_item, row_element) {
    //console.log(cell_item);
    var table_cell = document.createElement("td");
    var labels = cell_item["label_info"];
    for (i = 0; i < labels.length; i++) {
        var label_text = document.createElement("p");
        label_text.textContent = labels[i];
        table_cell.appendChild(label_text)
    };
    row_element.appendChild(table_cell);
};

//function build_row (plotinfo_list, tableID) {
function build_row (plotinfo_list, tableBodyID, indices = null) {
    //var textinfo_list = plotinfo_list[0];
    //var table = document.getElementById(tableID);
    var table_body = document.getElementById(tableBodyID);
    var table_row = document.createElement("tr");
    build_info_cell(plotinfo_list, table_row);
    //var plot_subdirs = plotinfo_list["plot_subdirs"];
    var plot_subdirs = select_subinfo(plotinfo_list["plot_subdirs"], indices);
    for (i = 0; i < plot_subdirs.length; i++) {
        build_image_cell(plot_subdirs[i], table_row)
    };
    table_body.appendChild(table_row)
};

function rebuild_row (plotinfo_list, tableBodyID, indices) {
    var info_subset = [];
    for (i = 0; i < indices.length; i++) {
        info_subset.push(plotinfo_list[i])
    };
    build_row(info_subset, tableBodyID)
};

function build_cell (cell_item, row_element) {
    var table_cell = document.createElement("td");
    table_cell.textContent = cell_item;
    row_element.appendChild(table_cell);
};

function build_image_cell (cell_item, row_element) {
    var table_cell = document.createElement("td");
    row_element.appendChild(table_cell);
    var link_element = document.createElement("a");
    link_element.href = cell_item;
    table_cell.appendChild(link_element);
    var image_element = document.createElement("img");
    image_element.src = cell_item;
    image_element.height = "200";
    image_element.width = "200";
    link_element.appendChild(image_element)
};

function reset_table_element (element_ID) {
    var table_element = document.getElementById(element_ID);
    table_element.innerHTML = "";
};

//function build_header_row (plotinfo_list, tableID) {
function build_header_row (plotinfo_list, tableHeadID, indices = null) {
    //var table = document.getElementById(tableID);
    //var table_head = document.getElementById(tableHeadID);
    //table_head.innerHTML = "";
    var table_head = document.getElementById(tableHeadID);
    var table_row = document.createElement("tr");
    build_cell("job info", table_row);
    //var plot_subdirs = plotinfo_list["plot_subdirs"];
    var plot_subdirs = select_subinfo(plotinfo_list["plot_subdirs"], indices);
    console.log(plot_subdirs);
    for (i = 0; i < plot_subdirs.length; i++) {
        //console.log(plotinfo_list[i]);
        //console.log(plotinfo_list);
        var column_info = plot_subdirs[i].split("/").pop();
        column_info = column_info.replace(/\.[^/.]+$/, "");
        column_info = column_info.replace(/_/g, " ");
        build_cell(column_info, table_row)
    };
    table_head.appendChild(table_row)
};

function select_subinfo (plotinfo_list, indices = null) {
    if (indices) {
        var info_subset = [];
        for (i = 0; i < indices.length; i++) {
            info_subset.push(plotinfo_list[i])
        }
    } else {
        info_subset = plotinfo_list
    };
    return info_subset
};

function rebuild_header_row (plotinfo_list, tableHeadID, indices) {
    reset_table_element (tableHeadID);
    //var info_subset = [];
    //console.log(indices);
    //for (i = 0; i < indices.length; i++) {
        //console.log(plotinfo_list[i]);
        //info_subset.push(plotinfo_list["plot_subdirs"][i])
    //};
    //console.log(info_subset);
    //build_header_row(info_subset, tableHeadID)
    build_header_row(plotinfo_list, tableHeadID, indices)
};

function build_table (jsonString, tableID, indices = null) {
    var jsonObject = JSON.parse(jsonString);
    var table_size = jsonObject.length;
    var single_page_limit = 100;
    if (single_page_limit < table_size) {
        table_size = single_page_limit
    };
    //console.log(jsonObject[0]);
    reset_table_element(tableID[1]);
    reset_table_element(tableID[2]);
    build_header_row(jsonObject[0], tableID[1], indices);
    for (j = 0; j < table_size; j++) {
        build_row(jsonObject[j], tableID[2], indices)
    };
};

//function build_table (jsonString, tableID) {
//    var jsonObject = JSON.parse(jsonString);
//    var table_size = jsonObject.length;
//    var single_page_limit = 100;
//    if (single_page_limit < table_size) {
//        table_size = single_page_limit
//    };
//    //console.log(jsonObject[0]);
//    reset_table_element(tableID[1]);
//    reset_table_element(tableID[2]);
//    build_header_row(jsonObject[0]["plot_subdirs"], tableID[1]);
//    for (j = 0; j < table_size; j++) {
//        build_row(jsonObject[j], tableID[2])
//    };
//};

function rebuild_table (jsonString, tableID) {
    var jsonObject = JSON.parse(jsonString);
    var table_size = jsonObject.length;
    var single_page_limit = 100;
    if (single_page_limit < table_size) {
        table_size = single_page_limit
    };
    console.log(jsonObject[0]);
    rebuild_header_row(jsonObject[0], tableID[1], [0, 2, 3]);
    //console.log(table_size);
    reset_table_element (tableBodyID);
    for (j = 0; j < table_size; j++) {
        rebuild_row(jsonObject[j], tableID[2], [0, 2, 3])
    };
};

function build_anonymous_function (function_name, table_info) {
    return function (jsonString) {
        function_name (jsonString, table_info)
    }
};

//function build_table_function (tableID) {
//    return function (jsonString) {
//        build_table (jsonString, tableID)
//    }
//}


function rebuild_table_function (table_info, indices) {
    return function (jsonString) {
        build_table (jsonString, table_info, indices)
    }
};
