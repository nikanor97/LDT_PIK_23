import * as React from "react";
import {Drawer, DrawerProps} from "antd";
import classnames from "classnames";
import styles from "./Drawer.module.less";
import {children} from "@types";

type iDrawerComponent = {
    antProps: Omit<DrawerProps, "children">
    children: children | children[];
}

const DrawerComponent = (props: iDrawerComponent) => {
    return React.createElement(
        Drawer, 
        {
            ...props.antProps,
            className: classnames(
                styles.drawer,
                props.antProps.className
            ),
        },
        props.children
    );
};

export default DrawerComponent;
