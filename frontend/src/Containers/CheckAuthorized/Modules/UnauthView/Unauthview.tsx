import React from "react";
import {Result, Button} from "antd";
import {Link} from "react-router-dom";
import routes from "@routes";

const UnauthView = () => {
    return (
        <Result
            status="warning"
            title="Недостаточно прав на просмотр страницы."
            extra={
                <Link
                    to={routes.auth.login}>
                    <Button
                        size="large"
                        color="primary">
                        Авторизоваться
                    </Button>
                </Link>
            }
        />
    );
};

export default UnauthView;
