import React from "react";
import {Switch, Route} from "react-router-dom";
import routes from "@routes";
import Pages from "@pages/index";

const ProjectRouter = () => {
    return (
        <Switch>
            <Route
                exact
                path={routes.lk.project.root()}>
                <Pages.Lk.Project />
            </Route>
            <Route path="*">
                <Pages.Undefined />
            </Route>
        </Switch>
    );
};

export default ProjectRouter;
