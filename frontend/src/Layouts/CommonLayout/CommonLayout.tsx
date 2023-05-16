import React from "react";
import {Layout} from "antd";
import {iLayoutProps} from "../index";

const CommonLayout = (props: iLayoutProps) => {

    return (
        <Layout className={props.layoutClassname}>
            <Layout.Content className={props.contentClassname}>
                {props.children}
            </Layout.Content>
        </Layout>
    );
};

export default CommonLayout;
