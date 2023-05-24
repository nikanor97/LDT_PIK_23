import React from "react";
import LogOut from "@assets/Icons/HeaderMenu/LogOut/LogOut";
import {useAppDispatch} from "@root/Hooks";
import Cookies from "universal-cookie";
import Actions from "@actions";
import styles from "./Menu.module.less";
import {Button} from "@components/Controls";

const cookies = new Cookies();

const MenuModule = () => {
    const dispatch = useAppDispatch();
    const logout = () => {
        dispatch(Actions.User.setFetching(true));
        cookies.remove("access_token", {path: "/"});
        cookies.remove("refresh_token", {path: "/"});
        dispatch(Actions.User.getUserInfo());
    };
    return (
        <div className={styles.wrapper}>
            <Button
                type="menu"
                className={styles.btn}
                onClick={logout}
                icon={<LogOut />}>
                Выход
            </Button>
        </div>
    );
};

export default MenuModule;
