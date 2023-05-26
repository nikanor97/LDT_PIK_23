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
  
const Tables: React.FC<TablesProps> = ({tables}) => {
    const columns = [
        {
            title: "Name",
            dataIndex: "name",
            key: "name",
        },
        {
            title: "Diameter 1",
            dataIndex: "diameter1",
            key: "diameter1",
        },
        {
            title: "Diameter 2",
            dataIndex: "diameter2",
            key: "diameter2",
        },
        {
            title: "Diameter 3",
            dataIndex: "diameter3",
            key: "diameter3",
        },
        {
            title: "Angle",
            dataIndex: "angle",
            key: "angle",
        },
        {
            title: "Direction",
            dataIndex: "direction",
            key: "direction",
        },
    ];
  
    return (
        <div className={styles.wrapper}>
            {tables.map((table, index) => (
                <>
                    <Title variant="h2" className={styles.title}>
                        {table.name}
                    </Title>
                    <Table
                        className={styles.table}
                        key={index} 
                        dataSource={table.values} 
                        columns={columns}
                        pagination={false}
                        size="small"
            
                    />
                </>

            ))}

        </div>
    );
};
  
export default Tables;
  
