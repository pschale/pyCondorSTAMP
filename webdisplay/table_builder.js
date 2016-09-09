function build_info_cell (cell_item, row_element) {
    var table_cell = document.createElement("td");
    var labels = cell_item["label_info"];
    for (i = 0; i < labels.length; i++) {
        var label_text = document.createElement("p");
        label_text.textContent = labels[i];
        table_cell.appendChild(label_text)
    };
    row_element.appendChild(table_cell);
};

function build_row (plotinfo_list, tableBodyID, indices = null) {
    var table_body = document.getElementById(tableBodyID);
    var table_row = document.createElement("tr");
    build_info_cell(plotinfo_list, table_row);
    var plot_subdirs = select_subinfo(plotinfo_list["plot_subdirs"], indices);
    for (i = 0; i < plot_subdirs.length; i++) {
        build_image_cell(plot_subdirs[i], table_row)
    };
    table_body.appendChild(table_row)
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

function reset_element (element_ID) {
    var element_object = document.getElementById(element_ID);
    element_object.innerHTML = "";
};

//function plotTitles (func_array, plotinfo_list, indices = null, second_arg = null, third_arg = null) {
function plotTitles (func, plotinfo_list, indices = null, second_arg = null, third_arg = null) {
    var plot_subdirs = select_subinfo(plotinfo_list["plot_subdirs"], indices);
    for (i = 0; i < plot_subdirs.length; i++) {
        var column_info = plot_subdirs[i].split("/").pop();
        column_info = column_info.replace(/\.[^/.]+$/, "");
        column_info = column_info.replace(/_/g," ");
        func(column_info, second_arg, third_arg)
        //for (j = 0; j < func_array.length; j++) {
            //func_array[j](column_info, second_arg, third_arg)
        //}
    }
};

function build_header_row (plotinfo_list, tableHeadID, indices = null) {
    var table_head = document.getElementById(tableHeadID);
    var table_row = document.createElement("tr");
    build_cell("job info", table_row);
    //plotTitles([build_cell], plotinfo_list, indices, table_row);
    plotTitles(build_cell, plotinfo_list, indices, table_row);
    table_head.appendChild(table_row)
};

function select_subinfo (plotinfo_list, indices = null) {
    if (indices) {
        var info_subset = [];
        for (i = 0; i < indices.length; i++) {
            info_subset.push(plotinfo_list[indices[i]])
        }
    } else {
        info_subset = plotinfo_list
    };
    return info_subset
};

function build_table (jsonString, tableID, indices = null, single_page_limit = 25) {
    var jsonObject = JSON.parse(jsonString);
    var table_size = jsonObject.length;
    if (single_page_limit < table_size) {
        table_size = single_page_limit
    };
    reset_element(tableID[1]);
    reset_element(tableID[2]);
    build_header_row(jsonObject[0], tableID[1], indices);
    for (j = 0; j < table_size; j++) {
        build_row(jsonObject[j], tableID[2], indices)
    };
};

function build_table_function (table_info) {
    return function (jsonString) {
        build_table (jsonString, table_info)
    }
};

function rebuild_table_function (table_info, indices) {
    return function (jsonString) {
        build_table (jsonString, table_info, indices)
    }
};
