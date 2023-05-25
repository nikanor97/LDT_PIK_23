import React, {useMemo} from "react";
import {iApi} from "@types";
import moment from "moment";
import TableFilters from "@components/TableFilters/TableFilters";
import {FilterDropdownProps} from "antd/es/table/interface";
import {useAppSelector} from "@root/Hooks";
import styles from "./useColumns.module.less";
import useGetMinColumnWidthForTable from "@root/Hooks/GetMinColumnWidthForTable/useGetMinColumnWidthForTable";
import Tooltip from "@root/Components/Tooltip/Tooltip";
import {Tag} from "antd";

type ProjectListItem = iApi.Projects.Item;

const momentFormat = "DD-MM-YYYY HH:mm:ss";

const useColumns = () => {
    const projects = useAppSelector((state) => state.Projects.projects);
    const getDataForFilters = (handler: (item:ProjectListItem) => string) => {
        return Array.from(
            new Set(
                projects?.map((item) => {
                    return handler(item);
                })
            )
        );
    };

    const dataFilterMapper = (item: string) => ({
        text: item,
        value: item,
    });

    const checkDate = (value: string) => {
        if (value === "Данные отсутствуют" || value === "-") {
            return value;
        } else {
            return moment(value).format(momentFormat);
        }
    };

    const checkStatus = (value: number) => {
        if (value === null || value === 100) {
            return "В процессе";
        } else if (value === 400) {
            return "Ошибка";
        } else {
            return "Готово";
        }
    };
    const nameFD = useMemo(() => getDataForFilters((item) => item.name), [projects]);
    const bathroomTypeFD = useMemo(() => getDataForFilters((item) => item.bathroomType), [projects]);
    const authorFD = useMemo(() => getDataForFilters((item) => item.author), [projects]);
    const performerFD = useMemo(() => getDataForFilters((item) => item.performer), [projects]);
    const statusFD = ["Готово", "В процессе", "Ошибка"];

    return [
        {
            title: "Название",
            dataIndex: "name",
            key: "name",
            filters: nameFD.map(dataFilterMapper),
            width: 250,
            render: (name: ProjectListItem["name"]) => 
                (
                    <span style={{
                        minWidth: useGetMinColumnWidthForTable("Название")
                    }}
                    className={styles.titleColumn}>
                        <Tooltip 
                            lineTooltip={true}
                            title={name}
                            placement="right">
                            {name}
                        </Tooltip>
                    </span>
                ),
            sorter: (first: ProjectListItem, second: ProjectListItem) =>
                first.name.localeCompare(second.name),
            showSorterTooltip: false,
            filterDropdown: (props: FilterDropdownProps) => {
                return <TableFilters {...props} />;
            },
            onFilter: (
                value: string | number | boolean,
                record: iApi.Projects.Item
            ) => record.name === value,
            ellipsis: true,
        },
        {
            title: "Автор задания",
            dataIndex: "author",
            key: "author",
            sorter: (first: ProjectListItem, second: ProjectListItem) =>
                first.author.localeCompare(
                    second.author
                ),
            showSorterTooltip: false,
            render: (author: ProjectListItem["author"]) => (
                <div style={{width: useGetMinColumnWidthForTable("Автор проекта")}}>
                    {author}
                </div>
            ),
            filters: authorFD.map(dataFilterMapper),
            filterDropdown: (props: FilterDropdownProps) => {
                return <TableFilters {...props} />;
            },
            onFilter: (
                value: string | number | boolean,
                record: iApi.Projects.Item
            ) => record.author === value,
            ellipsis: true,
        },
        {
            title: "Статус",
            dataIndex: "status",
            key: "status",
            sorter: (first: ProjectListItem, second: ProjectListItem) => first.status - second.status,
            render: (status: ProjectListItem["status"]) => {
                if (status === null || status === 100) {
                    return (
                        <Tag className={styles.tagProcess}>В процессе</Tag>
                    );
                } else if (status === 400) {
                    return (
                        <Tag className={styles.tagError}>Ошибка</Tag>
                    );
                } else {
                    return (
                        <Tag  className={styles.tagSuccess}>Готово</Tag>
                    );
                }
            },
            filters: statusFD.map(dataFilterMapper),
            showSorterTooltip: false,
            filterDropdown: (props: FilterDropdownProps) => {
                return (
                    <TableFilters
                        {...props}
                    />
                );
            },
            onFilter: (value: string | number | boolean, record: iApi.Projects.Item) => checkStatus(record.status) === value,
            ellipsis: true,
        },
        {
            title: "Тип Санузла",
            dataIndex: "bathroomType",
            key: "bathroomType",
            filters: bathroomTypeFD.map(dataFilterMapper),
            sorter: (first: ProjectListItem, second: ProjectListItem) =>
                first.bathroomType.localeCompare(
                    second.bathroomType
                ),
            showSorterTooltip: false,
            render: (doc_classified_doctype: ProjectListItem["bathroomType"]) => {
                return (
                    <div style={{minWidth: useGetMinColumnWidthForTable("Тип Санузла")}}>
                        {doc_classified_doctype}
                    </div>
                );
            },
            filterDropdown: (props: FilterDropdownProps) => {
                return <TableFilters {...props} />;
            },
            onFilter: (
                value: string | number | boolean,
                record: iApi.Projects.Item
            ) => record.bathroomType === value,
            ellipsis: true,
        },
        {
            title: "Исполнитель",
            dataIndex: "performer",
            key: "performer",
            sorter: (first: ProjectListItem, second: ProjectListItem) =>
                first.performer.localeCompare(
                    second.performer
                ),
            showSorterTooltip: false,
            render: (performer: ProjectListItem["performer"]) => (
                <div style={{width: useGetMinColumnWidthForTable("Исполнитель")}}>
                    {performer}
                </div>
            ),
            filters: performerFD.map(dataFilterMapper),
            filterDropdown: (props: FilterDropdownProps) => {
                return <TableFilters {...props} />;
            },
            onFilter: (
                value: string | number | boolean,
                record: iApi.Projects.Item
            ) => record.performer === value,
            ellipsis: true,
        },
    ];
};

export default useColumns;
