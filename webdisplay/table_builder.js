function build_info_cell (cell_item, row_element) {
    var table_cell = document.createElement("td");
    var labels = cell_item["label info"];
    for (i = 0; i < labels.length; i++) {
        var label_text = document.createElement("p");
        label_text.textContent = labels[i];
        table_cell.appendChild(label_text)
    };
    row_element.appendChild(table_cell);
};

function build_row (plotinfo_list, tableID) {
    var textinfo_list = plotinfo_list[0];
    var table = document.getElementById(tableID);
    var table_row = document.createElement("tr");
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
