import React from "react";
import styles from "./CountStatBlock.module.less";

type CountStatBlockProps = {
    icon: JSX.Element,
    title: string;
    statNumber: number | string;
}

const CountStatBlock = (props: CountStatBlockProps) => {
    return (
        <div className={styles.countStat}>
            <div>
                <div className={styles.icon}>
                    {props.icon}
                </div>
                <div className={styles.title}>
                    {props.title}
                </div>
            </div>
            {props.statNumber === 0 || props.statNumber === "0 м" ? (
                <div className={styles.countEmpty}>
                    {props.statNumber}
                </div>
            ) : (
                <div className={styles.count}>
                    {props.statNumber}
                </div>
            )}

        </div>
    );
};

export default CountStatBlock;
