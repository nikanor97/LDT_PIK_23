import React from "react";
import {Switch, Route} from "react-router-dom";
import Login from "../Contents/Login/Login";
import Registration from "../Contents/Registration/Registration";
import routes from "@routes";

const ContentController = () => {
    return (
        <Switch>
            <Route path={routes.auth.login}>
                <Login />
            </Route>
            <Route path={routes.auth.registration}>
                <Registration />
            </Route>
        </Switch>
    );
};

export default ContentController;
