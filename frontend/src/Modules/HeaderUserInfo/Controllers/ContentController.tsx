import React, {useMemo} from "react";
import {useAppSelector} from "@root/Hooks";
import {Guard} from "@types";
import AuthorisedView from "../Views/AuthorisedView/AuthorisedView";
import UnauthorisedView from "../Views/UnauthorisedView/UnauthorisedView";

const {isAuthUserInfo} = Guard.User;

const ContentController = () => {
    const userInfo = useAppSelector((state) => state.User.info);
    const isAuth = useMemo(() => isAuthUserInfo(userInfo), [userInfo]);
    if (isAuth) return <AuthorisedView userInfo={userInfo} />;
    else return <UnauthorisedView />;
};

export default ContentController;
