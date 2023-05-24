import React from "react";
import {Button as AntButton} from "antd";
import {ButtonProps} from "antd/lib/button";
import classNames from "classnames";
import "./Button.less";

export type iButtonProps = Omit<ButtonProps, "type"> & {
    type?: ButtonProps["type"] | "icon" | "secondary" | "stroke" | "menu";
};

const prefixCls = "btn";

const getButtonType = (type: iButtonProps["type"]): ButtonProps["type"] => {
    if (!type) return "default";
    if (type === "icon") return "primary";
    if (type === "secondary") return "default";
    if (type === "stroke") return "default";
    if (type === "menu") return "default";
    return type;
};

const Button = (props: iButtonProps) => {
    const {type} = props;
    const antType = getButtonType(type);

    const className = classNames(props.className, prefixCls, {
        [`${prefixCls}_icon`]: type === "icon" && !props.disabled,
        [`${prefixCls}_secondary`]: type === "secondary" && !props.disabled,
        [`${prefixCls}_stroke`]: type === "stroke" && !props.disabled,
        [`${prefixCls}_menu`]: type === "menu" && !props.disabled,
    });

    return React.createElement(AntButton, {
        ...props,
        type: antType,
        className,
    });
};

export default Button;
