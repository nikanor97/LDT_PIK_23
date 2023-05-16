import React, {useState} from "react";
import styles from "./DropdownMenu.module.less";
import {Popover} from "antd";
import {ButtonIcon} from "@root/Components/Controls";
import {MoreOutlined} from "@ant-design/icons";
import MenuModule, {MenuModuleItem} from "./Modules/MenuModule/MenuModule";

type DropdownMenuProps = {
    handlePopoverVisibleExpand?: Function;
    menuItems: MenuModuleItem[]
}

const DropdownMenu = (props: DropdownMenuProps) => {

    const [popover, setPopover] = useState<boolean>(false);

    const hidePopover = () => {
        setPopover(false);
    };
    const handlePopoverVisible = (visible: boolean) => {
        props.handlePopoverVisibleExpand && props.handlePopoverVisibleExpand();
        setPopover(visible);
    };

    return (
        <Popover
            key="more"
            content={
                <MenuModule 
                    hidePopover={hidePopover} 
                    menuItems={props.menuItems}/>
            }
            trigger="click"
            visible={popover}
            onVisibleChange={handlePopoverVisible}
            placement="bottomLeft"
            className={styles.popover}>
            <ButtonIcon
                type="text"
                icon={
                    <MoreOutlined 
                        style={{
                            fontSize: 20,
                            lineHeight: 0
                        }}/>
                }
                onClick={(e) => e.stopPropagation()}
                className={styles.button}
            />
        </Popover>
    );
};

export default DropdownMenu;
