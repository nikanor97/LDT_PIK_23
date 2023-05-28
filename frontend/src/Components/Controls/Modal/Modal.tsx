import * as React from "react";
import {Modal, ModalProps} from "antd";
import classnames from "classnames";
import styles from "./Modal.module.less";
import {children} from "@types";

type iModalComponent = {
    antProps: Omit<ModalProps, "children">
    children: children | children[];
}

const ModalComponent = (props: iModalComponent) => {
    return React.createElement(
        Modal, 
        {
            transitionName: props.antProps.visible ? "" : "animaion",
            maskTransitionName: "",
            ...props.antProps,
            className: classnames(
                styles.modal,
                props.antProps.className,
                props.antProps.visible 
                    ? styles.animationOn 
                    : styles.animationOut,
            ),
        },
        props.children
    );
};

export default ModalComponent;
