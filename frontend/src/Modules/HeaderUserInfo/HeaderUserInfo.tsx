import React from "react";
import {Row} from "antd";
import ContentController from "./Controllers/ContentController";

const HeaderUserInfo = () => {
    return (
        <div>
            <Row gutter={[25,0]}>
                <ContentController />
            </Row>
        </div>
    );
};

export default HeaderUserInfo;
