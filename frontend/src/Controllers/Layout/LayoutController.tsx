import React from "react";
import Layouts from "@layouts";
import {Switch, Route} from "react-router-dom";
import {children} from "@types";
import routes from "@routes";

export type iLayoutController = {
    children: children | children[]
};

const LayoutController = (props:iLayoutController) => {
    return (
        <Switch>
            <Route path={routes.lk.root}>
                <Layouts.LkLayout>
                    {props.children}
                </Layouts.LkLayout>
            </Route>
            <Route path="*">
                <Layouts.CommonLayout>
                    {props.children}
                </Layouts.CommonLayout>
            </Route>
        </Switch>
    );
};

export default LayoutController;
