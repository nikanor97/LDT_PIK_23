import React from "react";
import {Switch, Route} from "react-router-dom";
import routes from "@routes";
import Pages from "@pages/index";

const AuthRouter = () => {
    return (
        <Switch>
            <Route
                exact
                path={[
                    routes.auth.login,
                    routes.auth.registration,
                ]}>
                <Pages.Auth />
            </Route>
            <Route path="*">
                <Pages.Undefined />
            </Route>
        </Switch>
    );
};

export default AuthRouter;
