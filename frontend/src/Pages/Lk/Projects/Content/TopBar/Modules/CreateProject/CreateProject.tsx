import {Button} from "@components/Controls";
import Plus from "@root/Assets/Icons/Plus/Plus";
import React from "react";
import styles from "./CreateProject.module.less";

const CreateProject = () => {
    return (
        <Button
            type="primary"
            className={styles.button}
            icon={<Plus />}>
            Создать проект
        </Button>
    );
};

export default CreateProject;
