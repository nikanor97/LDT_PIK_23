import React from "react";
import styles from "./StatCard.module.less";
import classnames from "classnames";

type StatCardProps = {
    title: string;
    value: number;
    className?: string;
}

const StatCard = (props: StatCardProps) => {

    const classes = {
        wrapper: classnames(styles.wrapper, props.className)
    };
    
    return (
        <div className={classes.wrapper}>
            <div className={styles.title}>
                {props.title}
            </div>
            <div className={styles.value}>
                {props.value}
            </div>
        </div>
    );
};

export default StatCard;
