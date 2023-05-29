import React from "react";
import {Select, SelectProps} from "antd";
import styles from "./Select.module.less";
import classnames from "classnames";
import {SelectValue} from "antd/lib/select";

const SelectComponent = (props: SelectProps<SelectValue>) => {
    return React.createElement(
        Select,
        {
            ...props,
            className: classnames(
                props.className,
                styles.select
            )
        }
    );
};

SelectComponent.Option = Select.Option;

export default SelectComponent;
