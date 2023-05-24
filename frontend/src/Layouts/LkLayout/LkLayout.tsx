import React from "react";
import {Layout} from "antd";
import Header from "@modules/Header/Header";
import {iLayoutProps} from "../index";
import HeaderUserInfo from "@modules/HeaderUserInfo/HeaderUserInfo";
import styles from "./LKLayout.module.less";
import classnames from "classnames";

const LkLayout = (props: iLayoutProps) => {
    return (
        <Layout className={classnames(styles.layout, props.layoutClassname)}>
            <Layout>
                <Header AuthCol={<HeaderUserInfo />} />
                <Layout.Content className={classnames(styles.content, props.contentClassname)}>
                    {props.children}
                </Layout.Content>
            </Layout>
        </Layout>
    );
};

export default LkLayout;
