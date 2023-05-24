import React from "react";
import classnames from "classnames";
import styles from "./Title.module.less";

type iTitle = {
    variant: "h1" | "h2" | "h3"
    className?: string;
    children: string | JSX.Element;
}

const Title = (props: iTitle) => {
    const classes = {
        wrapper: classnames(
            styles[props.variant], 
            styles.common,
            props.className
        )
    };
    return (
        <div className={classes.wrapper}>
            {props.children}
        </div>
    );
};

export default Title;
