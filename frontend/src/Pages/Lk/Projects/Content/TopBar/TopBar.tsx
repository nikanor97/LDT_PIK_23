import React from "react";
import Title from "@root/Components/Title/Title";
import styles from "./TopBar.module.less";
import {useAppSelector} from "@root/Hooks";
import CreateProject from "./Modules/CreateProject/CreateProject";
import DeleteProjects from "./Modules/DeleteProjects/DeleteProjects";

const TopBar = () => {
    const projectsLength = useAppSelector((state) => state.Projects.projects?.length);

    return (
        <div className={styles.wrapper}>
            <div className={styles.info}>
                <Title
                    variant="h2"
                    className={styles.title}>
                    Проекты
                </Title>
                <div className={styles.subtext}>
                    всего {projectsLength ? projectsLength : 0}
                </div>
            </div>
            <div className={styles.buttons}>
                <DeleteProjects />
                <CreateProject />
            </div>
            
        </div>
    );
};

export default TopBar;
