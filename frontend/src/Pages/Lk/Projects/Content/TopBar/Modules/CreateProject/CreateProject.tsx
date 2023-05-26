import {Button} from "@components/Controls";
import Plus from "@root/Assets/Icons/Plus/Plus";
import React, {useEffect} from "react";
import styles from "./CreateProject.module.less";
import {useAppDispatch} from "@root/Hooks";
import Actions from "@actions";
import CreateProjectModal from "./Modules/CreateProjectModal/CreateProjectModal";

const CreateProject = () => {
    const dispatch = useAppDispatch();

    const onClick = () => {
        dispatch(Actions.Projects.setCreateModal(true));
    };

    return (
        <>
            <Button
                type="primary"
                className={styles.button}
                onClick={onClick}
                icon={<Plus />}>
                Создать проект
            </Button>
            <CreateProjectModal />
        </>

    );
};

export default CreateProject;
