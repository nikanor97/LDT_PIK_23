import React from "react";
import useGetMinColumnWidthForTable from "@root/Hooks/GetMinColumnWidthForTable/useGetMinColumnWidthForTable";

type TableData = {
    name: string,
    material_id: string,
    n_items: number,
    total_length: number,
}

const useColumns = () => {

    return [
        {
            title: "Наименование",
            dataIndex: "name",
            key: "name",
            width: 50,
            render: (name: TableData["name"]) => (
                <div style={{width: useGetMinColumnWidthForTable("Наименование")}}>
                    {name}
                </div>
            ),
        },
        {
            title: "ИД материала",
            dataIndex: "material_id",
            key: "material_id",
            width: 50,
            render: (material_id: TableData["material_id"]) => (
                <div style={{width: useGetMinColumnWidthForTable("ИД материала")}}>
                    {material_id}
                </div>
            ),
        },
        {
            title: "Количество",
            dataIndex: "n_items",
            key: "n_items",
            width: 50,
            render: (n_items: TableData["n_items"]) => (
                <div style={{width: useGetMinColumnWidthForTable("Количество")}}>
                    {n_items}
                </div>
            ),
        },
        // {
        //     title: "Длина",
        //     dataIndex: "total_length",
        //     key: "total_length",
        //     width: 50,
        //     render: (total_length: TableData["total_length"]) => (
        //         <div style={{width: useGetMinColumnWidthForTable("Длина")}}>
        //             {total_length}
        //         </div>
        //     ),
        // },
        
    ];
};

export default useColumns;
