import React from "react";
import {Table, Image, Row, Col} from "antd";
import styles from "./Graph.module.less";

type TableData = {
    id: number,
    graph: string;
    material: string;
    probability: number;
}

type DataObject = {
    table: TableData[];
    image: string;
}

type GraphTabProps = {
    data: DataObject;
}

const GraphTab = (props: GraphTabProps) => {
    const {data} = props;
    
    const columns = [
        {
            title: "Граф",
            dataIndex: "graph",
            key: "graph",
        },
        {
            title: "Материал",
            dataIndex: "material",
            key: "material",
        },
        {
            title: "Вероятность",
            dataIndex: "probability",
            key: "probability",
        },
    ];

    return (
        <Row gutter={24} className={styles.row}>
            <Col span={12}>
                <Table
                    className={styles.table}
                    dataSource={data.table}
                    columns={columns}
                    pagination={false}
                    scroll={{
                        y: "calc(100vh - 270px)",
                        x: true,
                    }}
                    size="small"
                    rowKey="id"
                />
            </Col>
            <Col span={12}>
                <Image
                    className={styles.image}
                    src={`data:image/png;base64,${data.image}`}
                />
            </Col>
        </Row>
    );
};

export default GraphTab;
