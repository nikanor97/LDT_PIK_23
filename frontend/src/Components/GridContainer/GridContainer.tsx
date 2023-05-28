import React from "react";
import styles from "./GridContainder.module.less";
import classNames from "classnames";
import {children} from "@types";

type iGridContainerProps = {
    children: children;
    className?: string;
}

const GridContainer = (props:iGridContainerProps) => {
    const classes = {
        wrapper: classNames(
            styles.container,
            props.className,
        )
    };
    return (
        <div
            className={classes.wrapper}>
            {props.children}
        </div>
    );
};

export default GridContainer;
