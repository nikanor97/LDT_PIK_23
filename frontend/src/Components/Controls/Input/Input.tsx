import React from "react";
import {Input, InputProps} from "antd";
import classnames from "classnames";
import styles from "./Input.module.less";
import {TextAreaProps, PasswordProps} from "antd/lib/input";

const InputComponent = (props: InputProps) => {
    return React.createElement(
        Input,
        {
            ...props,
            className: classnames(
                props.className,
                styles.input
            )
        }
    );
};

const TextArea = (props: TextAreaProps) => {
    return React.createElement(
        Input.TextArea,
        {
            ...props,
            className: classnames(
                props.className,
                styles.input
            )
        }
    );
};

const Password = (props: PasswordProps) => {
    return React.createElement(
        Input.Password,
        {
            ...props,
            className: classnames(
                props.className,
                styles.input
            )
        }
    );
};

InputComponent.TextArea = TextArea;
InputComponent.Password = Password;

export default InputComponent;
