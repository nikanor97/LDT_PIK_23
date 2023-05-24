import React, {useMemo} from "react";
import {useAppSelector} from "@root/Hooks";
import {Guard} from "@types";
import UnauthView from "./Modules/UnauthView/Unauthview";

const {isAuthUserInfo} = Guard.User;

type CheckAuthorizedProps = {
    children: JSX.Element,
    unauthView: JSX.Element
}

const CheckAuthorized = (props: CheckAuthorizedProps) => {
    const {children, unauthView} = props;
    const userInfo = useAppSelector((state) => state.User.info);
    const isAuth = useMemo(() => isAuthUserInfo(userInfo), [userInfo]);

    console.log(isAuth);

    return (
        <>
            {isAuth
                ? children
                : unauthView}
        </>
    );
};

CheckAuthorized.defaultProps = {
    unauthView: <UnauthView />,
};

export default CheckAuthorized;
