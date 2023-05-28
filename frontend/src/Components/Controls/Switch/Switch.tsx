import React from "react";
import {Switch, SwitchProps} from "antd";
import classnames from "classnames";
import styles from "./Switch.module.less";

const SwitchComponent = (props: SwitchProps) => {
    return React.createElement(
        Switch,
        {
            ...props,
            className: classnames(
                props.className,
                styles.switch
            )
        }
    );
};

export default SwitchComponent;
