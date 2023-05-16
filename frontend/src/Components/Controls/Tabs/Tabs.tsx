import React from "react";
import {Tabs, TabsProps, TabPaneProps} from "antd";
import classnames from "classnames";
import styles from "./Tabs.module.less";

const TabsComponent = (props: TabsProps) => {
    return React.createElement(
        Tabs,
        {
            ...props,
            className: classnames(
                props.className,
                styles.tabs
            )
        }
    );
};

const PaneComponent = (props: TabPaneProps) => {
    return React.createElement(
        Tabs.TabPane,
        {
            ...props,
            className: classnames(
                props.className,
                styles.pane
            )
        }
    );
};

TabsComponent.TabPane = PaneComponent;

export default TabsComponent;
