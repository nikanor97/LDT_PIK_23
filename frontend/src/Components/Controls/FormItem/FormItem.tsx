import React from "react";
import {Form, FormItemProps} from "antd";
import styles from "./FormItem.module.less";
import classnames from "classnames";

const FormItem = (props: FormItemProps) => {
    return React.createElement(
        Form.Item,
        {
            ...props,
            className: classnames(styles.wrapper, props.className)
        }
    );
};

export default FormItem;

