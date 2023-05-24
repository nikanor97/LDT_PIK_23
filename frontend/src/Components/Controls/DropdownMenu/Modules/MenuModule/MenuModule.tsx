import React from "react";
import styles from "./MenuModule.module.less";
import {Button} from "@root/Components/Controls";

type MenuModuleProps = {
    hidePopover: () => void;
    menuItems: MenuModuleItem[];
}

export type MenuModuleItem = {
    openModalFunc: Function;
    title: string;
    icon: JSX.Element
}

const MenuModule = (props: MenuModuleProps) => {

    return (
        <div className={styles.wrapper}>
            {
                props.menuItems.map((item, key) => {
                    return (
                        <Button
                            key={key}
                            type="menu"
                            className={styles.btn}
                            onClick={(e) => {
                                e.stopPropagation();
                                props.hidePopover();
                                item.openModalFunc();
                            }}
                            icon={item.icon}>
                            {item.title}
                        </Button>
                    );
                })
            }
        </div>
    );
};

export default MenuModule;
