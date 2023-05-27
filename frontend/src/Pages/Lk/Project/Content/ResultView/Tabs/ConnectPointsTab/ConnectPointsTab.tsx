import React from "react";
import {Table, Image, Row, Col} from "antd";
import {ColumnsType} from "antd/es/table";
import styles from "./ConnectPointsTab.module.less";

type TableData = {
    id: number,
    order: string;
    type: string;
    diameter: number;
    X: number;
    Y: number;
    Z: number;
}

type DataObject = {
    table: TableData[];
    image: string;
}

type ConnectPointsTabProps = {
    data: DataObject;
}

const ConnectPointsTab = (props: ConnectPointsTabProps) => {
    const {data} = props;
    const columns: ColumnsType<TableData> = [
        {
            title: "Порядок",
            dataIndex: "order",
            key: "order",
        },
        {
            title: "Тип",
            dataIndex: "type",
            key: "type",
        },
        {
            title: "Диаметр",
            dataIndex: "diameter",
            key: "diameter",
        },
        {
            title: "X",
            dataIndex: "X",
            key: "X",
        },
        {
            title: "Y",
            dataIndex: "Y",
            key: "Y",
        },
        {
            title: "Z",
            dataIndex: "Z",
            key: "Z",
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

export default ConnectPointsTab;
