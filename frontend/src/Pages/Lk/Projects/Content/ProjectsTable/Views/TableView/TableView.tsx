import React, {useEffect, useState} from "react";
import useColumns from "../../Hooks/useColumns";
import  {
    useGetValidNoun,
    useAppDispatch,
    useAppSelector,
    useNotification
} from "@root/Hooks";
import Actions from "@actions";
import {Table} from "antd";
import styles from "./TableView.module.less";
import routes from "@routes";
import {useHistory} from "react-router-dom";
import {iApi} from "@root/types";
import EmptyDocuments from "@root/Assets/Icons/EmptyDocuments/EmptyDocuments";

const TableView = () => {
    const projects = useAppSelector((state) => state.Projects.projects);
    const tableConfig = useAppSelector((state) => state.Projects.tableConfig);
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
            dispatch(Actions.Projects.setSelectedProjects(selectedRowKeys));
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

    // useEffect(() => {
    //     dispatch(Actions.Projects.getStatistics());
    // }, [projects]);

    if (!projects) return null;

    return (
        <Table
            rowSelection={rowSelection}
            onRow={(record) => {
                if (record.status === 100) {
                    return {
                        onClick: () => {
                            notification({
                                type: "info",
                                message: "Подождите, еще происходит расчёт"
                            });
                        },
                    };
                } else {
                    return {
                        onClick: () => {
                            history.push(routes.lk.project.root(record.id.toString()));
                        },
                    };
                }

            }}
            className={styles.table}
            dataSource={projects}
            columns={columns}
            pagination={{
                current: tableConfig ? tableConfig.currentPage : 1,
                defaultPageSize: tableConfig ? tableConfig.defaultPageSize : 10,
                pageSizeOptions: ["10", "20", "50"],
                showSizeChanger: true,
                locale: {items_per_page: ""},
                showTotal: (total) =>
                    <div className={styles.paginationTotal}>
                            Всего {total} {useGetValidNoun({
                            nounTypes,
                            number: total,
                        })}
                    </div>
                ,
                selectPrefixCls: styles.test,
            }}
            onChange={(config) => {
                if (!config.current || !config.pageSize) return; 
                dispatch(Actions.Projects.setTableConfig({
                    config: {
                        currentPage: config.current,
                        defaultPageSize: config.pageSize
                    },
                }));
            }}
            scroll={{
                y: "calc(100vh - 555px)",
                x: true,
            }}
            rowKey="id"
            size="small"
            locale={{emptyText: (<EmptyDocuments />)}}
        />        
    );
};

export default TableView;
