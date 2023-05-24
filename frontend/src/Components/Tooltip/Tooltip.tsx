import {Tooltip as AntTooltip, TooltipProps as AntTooltipProps} from "antd";
import React from "react";
import styles from "./Tooltip.module.less";
import classNames from "classnames";

type TooltipProps = React.PropsWithChildren<{
  lineTooltip?: boolean,
}> & AntTooltipProps

const Tooltip = (props: TooltipProps) => {
    const position = props.placement === undefined ? "bottom" : props.placement;
    return (
        <AntTooltip 
            {...props}
            placement={position}
            overlayClassName={classNames(
                styles.defaultToolTip,
                props.className,
                {[styles.lineTooltip]: props.lineTooltip},
                {[styles.bottom]: position.includes("bottom")},
                {[styles.right]: position.includes("right")}
            )}>
            {props.children}
        </AntTooltip>
    );
};
export default Tooltip;
