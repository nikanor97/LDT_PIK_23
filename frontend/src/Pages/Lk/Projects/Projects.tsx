import React, {useEffect} from "react";
import {useAppDispatch} from "@root/Hooks";
import Actions from "@actions";
import ProjectsTable from "./Content/ProjectsTable/ProjectsTable";
import styles from "./Projects.module.less";

const Projects = () => {
    const dispatch = useAppDispatch();

    useEffect(() => {
        dispatch(Actions.Projects.getProjects());
    }, []);

    return (
        <div className={styles.wrapper}>
            <ProjectsTable />
        </div>
    );
};

export default Projects;
