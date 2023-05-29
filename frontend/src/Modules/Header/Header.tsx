import React from "react";
import {Layout} from "antd";
import styles from "./Header.module.less";
import GridContainer from "@components/GridContainer/GridContainer";
import Logo from "@root/Assets/Logo/Logo";

interface iHeaderProps {
    AuthCol: JSX.Element | null;
}

const Header = (props: iHeaderProps) => {
    const {AuthCol} = props;

    return (
        <Layout.Header className={styles.wrapper}>
            <GridContainer className={styles.grid}>
                <div className={styles.row}>
                    <div className={styles.logo}>
                        <Logo />
                    </div>
                    <div className={styles.authCol}>
                        {AuthCol}
                    </div>
                </div>
            </GridContainer>
        </Layout.Header>
    );
};

export default Header;
