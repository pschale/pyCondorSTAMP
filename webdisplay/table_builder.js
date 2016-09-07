function isNumber(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
};

function splice_info (info_list) {
    var val_label = info_list[0];
    var value = info_list[1];
    if (isNumber(value)) {
        var label_string = val_label + value.toFixed(2)
    } else {
        var label_string = val_label + value
    };
    console.log(label_string);
    return label_string
};

function build_info_cell (cell_item, row_element) {
    var table_cell = document.createElement("td");
    var labels = [];
    console.log(cell_item.length);
    for (i = 0; i < cell_item.length; i++) {
        labels.push(splice_info(cell_item[i]))
    };
    console.log("labels");
    console.log(cell_item);
    console.log(labels);
    table_cell.textContent = labels.join("<br/>");
    row_element.appendChild(table_cell);
};

function build_row (plotinfo_list, tableID) {
    var textinfo_list = plotinfo_list[0];
    //var snr_info = textinfo_list[0];
    var table = document.getElementById(tableID);
    var table_row = document.createElement("tr");
    //var label_string = "SNR = " + snr_info.toFixed(2);
    console.log("build info cell");
    build_info_cell(textinfo_list, table_row);
    for (i = 1; i < plotinfo_list.length; i++) {
        build_image_cell(plotinfo_list[i], table_row)
    };
    table.appendChild(table_row)
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

function build_header_row (plotinfo_list, tableID) {
    var table = document.getElementById(tableID);
    var table_row = document.createElement("tr");
    build_cell("job info", table_row);
    for (i = 1; i < plotinfo_list.length; i++) {
        var column_info = plotinfo_list[i].split("/").pop();
        column_info = column_info.replace(/\.[^/.]+$/, "");
        column_info = column_info.replace(/_/g, " ");
        build_cell(column_info, table_row)
    };
    table.appendChild(table_row)
};

function build_table_function (tableID) {
    return function (jsonString) {
        var jsonObject = JSON.parse(jsonString);
        var table_size = jsonObject.length;
        var single_page_limit = 100;
        if (single_page_limit < table_size) {
            table_size = single_page_limit
        };
        build_header_row(jsonObject[0], tableID);
        for (j = 0; j < table_size; j++) {
            build_row(jsonObject[j], tableID)
        };
    }
}
