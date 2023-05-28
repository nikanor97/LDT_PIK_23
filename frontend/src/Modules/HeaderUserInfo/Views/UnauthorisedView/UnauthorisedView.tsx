import React from "react";
import {Col} from "antd";
import {Link} from "react-router-dom";
import routes from "@routes";

const AuthorisedView = () => {
    return (
        <>
            <Col>
                <div>
                    <Link to={routes.auth.login}>
                        Войти
                    </Link>
                </div>
            </Col>
        </>
    );
};
export default AuthorisedView;
