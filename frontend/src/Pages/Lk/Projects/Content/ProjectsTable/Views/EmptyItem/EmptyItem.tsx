import React from "react";
import {Empty} from "antd";
import EmptyDocuments from "@root/Assets/Icons/EmptyDocuments/EmptyDocuments";

const EmptyItem = () => {
    return (
        <Empty
            imageStyle={{height: "200px",
                width: "200px",
                margin: "auto"}}
            image={<EmptyDocuments />}
            description="Отсутствуют проекты"
        />
    );
};

export default EmptyItem;
