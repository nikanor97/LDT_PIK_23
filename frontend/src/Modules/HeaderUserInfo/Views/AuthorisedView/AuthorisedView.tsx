import React, {useEffect} from "react";
import {Col, Dropdown, Avatar} from "antd";
import {iApi, Guard} from "@types";
import Menu from "./Modules/Menu/Menu";
import styles from "./AuthorisedView.module.less";

const {isAuthUserInfo} = Guard.User;

type AuthorisedViewProps = {
    userInfo: iApi.User.iUserInfo | null
}

const AuthorisedView = (props: AuthorisedViewProps) => {
    const {userInfo} = props;

    if (!isAuthUserInfo(userInfo)) return null;
    return (
        <>
            <Col className={styles.col}>
                <div className={styles.name}>
                    {userInfo.name}
                </div>
                <Dropdown 
                    trigger={["click"]}
                    overlay={<Menu />}>
                    <Avatar className={styles.avatar}>
                        {userInfo.name[0].toUpperCase()}
                    </Avatar>
                </Dropdown>
            </Col>
        </>
    );
};
export default AuthorisedView;
