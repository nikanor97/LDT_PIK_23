import React from "react";
import {Input} from "antd";
import styles from "./Search.module.less";
import {SearchProps} from "antd/lib/input";

const Search = (props: SearchProps) => {
    return (
        <Input.Search 
            {...props}
            enterButton
            className={styles.search}
            allowClear
        />
    );
};

export default Search;
