import React from "react";
import {Button as AntButton} from "antd";
import {ButtonProps} from "antd/lib/button";
import classNames from "classnames";
import "./ButtonIcon.less";

export type iButtonProps = Omit<ButtonProps, "type"> & {
    type?: ButtonProps["type"] | "secondary" | "stroke";
}

const prefixCls = "btn-icon";

const getButtonType = (type: iButtonProps["type"]):ButtonProps["type"] => {
    if (!type) return "default";
    if (type === "secondary") return "default";
    if (type === "stroke") return "default";
    return type;
};

const ButtonIcon = (props:iButtonProps) => {
    const {type} = props;
    const antType = getButtonType(type);

    const className = classNames(
        props.className,
        prefixCls,
        {
            [`${prefixCls}_secondary`]: type === "secondary" && !props.disabled,
            [`${prefixCls}_stroke`]: type === "stroke" && !props.disabled,
        }
    );

    return React.createElement(AntButton,{
        ...props,
        type: antType,
        className
    });
};

export default ButtonIcon;
