import React from "react";
import useGetMinColumnWidthForTable from "@root/Hooks/GetMinColumnWidthForTable/useGetMinColumnWidthForTable";

type TableData = {
    id: number,
    order: string;
    type: string;
    diameter: number;
    coord_x: number;
    coord_y: number;
    coord_z: number;
}

const useColumns = () => {

    return [
        {
            title: "Порядок",
            dataIndex: "order",
            key: "order",
            width: 150,
            render: (order: TableData["order"]) => (
                <div style={{width: useGetMinColumnWidthForTable("Порядок")}}>
                    {order}
                </div>
            ),
        },
        {
            title: "Тип",
            dataIndex: "type",
            key: "type",
            width: 150,
            render: (type: TableData["type"]) => (
                <div style={{width: useGetMinColumnWidthForTable("Тип")}}>
                    {type}
                </div>
            ),
        },
        {
            title: "Диаметр",
            dataIndex: "diameter",
            key: "diameter",
            width: 150,
            render: (diameter: TableData["diameter"]) => (
                <div style={{width: useGetMinColumnWidthForTable("diameter")}}>
                    {diameter}
                </div>
            ),
        },
        {
            title: "X",
            dataIndex: "coord_x",
            key: "coord_x",
            width: 50,
            render: (coord_x: TableData["coord_x"]) => (
                <div>
                    {coord_x}
                </div>
            ),
        },
        {
            title: "Y",
            dataIndex: "coord_y",
            key: "coord_y",
            width: 50,
            render: (coord_y: TableData["coord_y"]) => (
                <div>
                    {coord_y}
                </div>
            ),
        },
        {
            title: "Z",
            dataIndex: "coord_z",
            key: "coord_z",
            width: 50,
            render: (coord_z: TableData["coord_z"]) => (
                <div>
                    {coord_z}
                </div>
            ),
        },
        
    ];
};

export default useColumns;
