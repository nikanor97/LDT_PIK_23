import React from "react";
import {Table} from "antd";
import Title from "@root/Components/Title/Title";
import styles from "./MaterialTab.module.less";
import Scrollbars from "react-custom-scrollbars";

interface TableValue {
    id: number;
    name: string;
    diameter1: number;
    diameter2: number;
    diameter3: number;
    angle: number;
    direction: string;
  }
  
  interface TableData {
    name: string;
    values: TableValue[];
  }
  
  interface TablesProps {
    tables: TableData[];
  }
  
const MaterialTab: React.FC<TablesProps> = ({tables}) => {
    const columns = [
        {
            title: "ИД",
            dataIndex: "id",
            key: "id",
        },
        {
            title: "Наименование",
            dataIndex: "name",
            key: "name",
        },
        {
            title: "Диаметр 1",
            dataIndex: "diameter1",
            key: "diameter1",
        },
        {
            title: "Диаметр 2",
            dataIndex: "diameter2",
            key: "diameter2",
        },
        {
            title: "Диаметр 3",
            dataIndex: "diameter3",
            key: "diameter3",
        },
        {
            title: "Угол",
            dataIndex: "angle",
            key: "angle",
        },
        {
            title: "Направление",
            dataIndex: "direction",
            key: "direction",
        },
    ];
  
    return (
        <div className={styles.wrapper}>
            {tables.map((table, key) => (
                <div key={key}>
                    <Title variant="h2" className={styles.title}>
                        {table.name}
                    </Title>
                    <Table
                        className={styles.table}
                        dataSource={table.values} 
                        columns={columns}
                        pagination={false}
                        size="small"
                        rowKey="name"
                    />
                </div>

            ))}

        </div>
    );
};
  
export default MaterialTab;
  
