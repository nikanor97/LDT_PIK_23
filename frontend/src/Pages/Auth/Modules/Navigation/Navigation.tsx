import React from "react";
import styles from "./Navigation.module.less";
import {Link} from "react-router-dom";

type NavigationProps = {
    route: string;
    children: string | JSX.Element;
}

const Navigation = (props: NavigationProps) => {
    const {route} = props;

    return (
        <Link
            to={route}
            className={styles.button}>
            {props.children}
        </Link>
    );
};

export default Navigation;
