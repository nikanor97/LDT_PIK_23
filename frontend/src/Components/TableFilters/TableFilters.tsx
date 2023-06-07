import React, {useState, useMemo} from "react";
import {Form, Checkbox, Col, Row, Space, Empty} from "antd";
import {Button, Search} from "@components/Controls";
import {FilterDropdownProps} from "antd/es/table/interface";
import {Scrollbars} from "react-custom-scrollbars";
import {CheckboxChangeEvent} from "antd/lib/checkbox";
import Hightlight from "react-highlight-words";
import Icon from "@ant-design/icons";
import styles from "./TableFilters.module.less";
import Tooltip from "../Tooltip/Tooltip";
import EmptyDocuments from "@root/Assets/Icons/EmptyDocuments/EmptyDocuments";

type iTableFilters =  FilterDropdownProps;

const TableFilters = (props:iTableFilters) => {
    const [search, setSearch] = useState("");
    const filteredData = useMemo(() => {
        if (!props.filters) return [];
        return props
            .filters
            .filter((item) => {
                return item.text
                ?.toString()
                .toLowerCase()
                .includes(search);
            });
    }, [props.filters, search]);

    const addValue = (value: string) => {
        props.setSelectedKeys([
            ...props.selectedKeys,
            value
        ]);
    };

    const deleteValue = (value: string) => {
        props.setSelectedKeys(
            props.selectedKeys.filter((item) => item !== value)
        );
    };
    const onCheckboxChange = (event:CheckboxChangeEvent, value: string) => {
        const checked = event.target.checked;
        if (checked) addValue(value);
        else deleteValue(value);
    };
    return (
        <div className={styles.wrapper}>
            <Form layout="vertical">
                <Form.Item
                    noStyle
                    label="Поиск по элементам">
                    <span className={styles.input}>
                        <Search
                            onChange={(event) => setSearch(event.target.value.toLowerCase())}
                        />
                    </span>
                </Form.Item>
                <Scrollbars
                    autoHeightMin={200}
                    autoHeightMax={200}
                    autoHeight>
                    <div className={styles.content}>
                        <Space
                            size={10}
                            className={styles.space}
                            direction="vertical">
                            {
                                filteredData.length
                                    ? filteredData
                                        .map((item, index) => (
                                            <Row key={index}>
                                                <Checkbox
                                                    onChange={(event) => onCheckboxChange(event, item.value.toString())}
                                                    checked={props.selectedKeys.includes(item.value.toString())}
                                                    className={styles.checkbox}>
                                                    {item.text?.toString() && item.text?.toString().length > 25 ? <>
                                                        <Tooltip
                                                            title={item?.text?.toString()}
                                                            placement="right"
                                                            lineTooltip={true}>
                                                            <Hightlight
                                                                highlightStyle={{
                                                                    padding: 0,
                                                                    backgroundColor: "#00D98B",
                                                                }}
                                                                searchWords={[search]}
                                                                autoEscape
                                                                textToHighlight={item.text?.toString() || ""}
                                                            />
                                                        </Tooltip>
                                                    </> : <>
                                                        <Hightlight
                                                            highlightStyle={{
                                                                padding: 0,
                                                                backgroundColor: "#00D98B",
                                                            }}
                                                            searchWords={[search]}
                                                            autoEscape
                                                            textToHighlight={item.text?.toString() || ""}
                                                        />
                                                    </> }
                                                </Checkbox>
                                                
                                            </Row>
                                        ))
                                    : (
                                        <Empty
                                            className={styles.empty}
                                            description="Совпадений не найдено"
                                            image={<Icon component={EmptyDocuments}/>}
                                        />
                                    )
                            }
                        </Space>
                    </div>
                </Scrollbars>
                <Row
                    className={styles.buttonsRow}>
                    <Col>
                        <div className={styles.buttons}>
                            <Button
                                className={styles.resetButton}
                                onClick={() => {
                                    if (props.clearFilters) props.clearFilters();
                                }}
                                type="ghost">
                                Сбросить
                            </Button>
                            <Button
                                onClick={() => props.confirm()}
                                type="primary">
                                Применить
                            </Button>
                        </div>
                    </Col>
                </Row>
            </Form>
        </div>
    );
};

export default TableFilters;
