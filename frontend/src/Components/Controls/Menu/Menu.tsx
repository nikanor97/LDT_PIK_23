import React from "react";
import {Menu, MenuProps, MenuItemProps} from "antd";
import classnames from "classnames";
import styles from "./Menu.module.less";
import MenuItem from "antd/lib/menu/MenuItem";
import ActiveIcon from "./Icons/Tick";

class MenuItemComponent extends MenuItem {
    constructor(props: MenuItemProps) {
        super(props);
    }

    render(): JSX.Element {
        return React.createElement(
            Menu.Item,
            {
                ...this.props,
                className: classnames(
                    styles.item,
                    this.props.className
                )
            },
            (
                <>
                    <span className={styles.activeIcon}>
                        <ActiveIcon />
                    </span>
                    {this.props.children}
                </>
            )
        );
    }
}

class MenuComponent extends Menu {
    constructor(props: MenuProps) {
        super(props);
    }

    static Item = MenuItemComponent;

    render(): JSX.Element {

        return React.createElement(
            Menu,
            {
                ...this.props,
                className: classnames(
                    styles.menu,
                    this.props.className
                )
            }
        );
    }
}

export default MenuComponent;
