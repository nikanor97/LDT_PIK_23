import React, {useEffect} from "react";
import {useAppDispatch} from "@root/Hooks";
import Actions from "@actions";
import ProjectsTable from "./Content/ProjectsTable/ProjectsTable";
import styles from "./Projects.module.less";
import TopBar from "./Content/TopBar/TopBar";
import StatBar from "./Content/StatBar/StatBar";

const Projects = () => {
    const dispatch = useAppDispatch();

    useEffect(() => {
        dispatch(Actions.Projects.getProjects());
        dispatch(Actions.User.getUsersAll());
        dispatch(Actions.Projects.getFittings());
        dispatch(Actions.Projects.getStatistics());
    }, []);

    return (
        <div className={styles.wrapper}>
            <TopBar />
            <StatBar />
            <ProjectsTable />
        </div>
    );
};

export default Projects;
