import {children} from "@root/types";
import React from "react";
import styles from "./Error.module.less";

type iErrorView = {
    children: children | children[];
}

const ErrorView = (props: iErrorView) => {
    return (
        <div className={styles.wrapper}>
            {props.children}
        </div>
    );
};

export default ErrorView;

