import React from "react";
import {Checkbox, CheckboxProps} from "antd";
import styles from "./Checkbox.module.less";
import classnames from "classnames";

const CheckboxCustom = (props: CheckboxProps) => {
    return React.createElement(
        Checkbox,
        {
            ...props,
            className: classnames(
                props.className,
                styles.wrapper
            )
        }
    );
};

export default CheckboxCustom;
