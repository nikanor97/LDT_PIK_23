import React from "react";
import {Switch, Route, Redirect} from "react-router-dom";
import routes from "@routes";
import Pages from "@pages/index";
import AuthRouter from "./Auth/AuthRouter";
import CheckAuthorized from "@containers/CheckAuthorized/CheckAuthorized";

const RoutesController = () => {
    return (
        <Switch>
            <Route exact path="/">
                <CheckAuthorized
                    unauthView={<Redirect to={routes.auth.login} />}>
                    <Redirect to={routes.lk.projects} />
                </CheckAuthorized>
            </Route>
            <Route path={routes.auth.root}>
                <CheckAuthorized
                    unauthView={<AuthRouter />}>
                    <Redirect to={routes.lk.projects} />
                </CheckAuthorized>
            </Route>
            <Route
                exact
                path={routes.lk.projects}>
                <CheckAuthorized
                    unauthView={<Redirect to={routes.auth.login} />}>
                    <Pages.Lk.Projects />
                </CheckAuthorized>
            </Route>
            <Route path="*">
                <Pages.Undefined />
            </Route>
        </Switch>
    );
};

export default RoutesController;
