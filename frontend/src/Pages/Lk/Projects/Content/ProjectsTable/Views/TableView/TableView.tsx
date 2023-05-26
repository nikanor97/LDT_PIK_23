import React, {useEffect} from "react";
import useColumns from "../../Hooks/useColumns";
import  {
    useGetValidNoun,
    useAppDispatch,
    useAppSelector
} from "@root/Hooks";
import Actions from "@actions";
import {Table} from "antd";
import styles from "./TableView.module.less";
import routes from "@routes";
import {useHistory} from "react-router-dom";
import {iApi} from "@root/types";
import EmptyDocuments from "@root/Assets/Icons/EmptyDocuments/EmptyDocuments";
import useNotification from "@root/Hooks/useNotification/useNotification";

const TableView = () => {

    const projects = useAppSelector((state) => state.Projects.projects);
    const columns = useColumns();
    const history = useHistory();
    const dispatch = useAppDispatch();
    const notification = useNotification();
    const nounTypes = {
        type1: "проект",
        type2: "проекта",
        type3: "проектов",
    };

    const rowSelection = {
        onChange: (selectedRowKeys: React.Key[], selectedRows: iApi.Projects.Item[]) => {
            dispatch(Actions.Projects.setSelectedProjects(selectedRows));
        },
        getCheckboxProps: (record: iApi.Projects.Item) => ({
            name: record.name,
        }),
    };

    useEffect(() => {
        return () => {
            dispatch(Actions.Projects.eraseSelectedProjects());
        };
    }, []);

    if (!projects) return null;

    return (
        <Table
            // rowSelection={rowSelection}
            className={styles.table}
            dataSource={projects}
            columns={columns}
            pagination={{
                defaultPageSize: 10,
                pageSizeOptions: ["10", "20", "50"],
                showSizeChanger: true,
                locale: {items_per_page: ""},
                showTotal: (total) =>
                    `Всего ${total} ${useGetValidNoun({
                        nounTypes,
                        number: total,
                    })}`,
                selectPrefixCls: styles.test,
            }}
            scroll={{
                y: "calc(100vh - 477px)",
                x: true,
            }}
            rowKey="id"
            size="small"
            locale={{emptyText: (<EmptyDocuments />)}}
            
        />
    );
};

export default TableView;
