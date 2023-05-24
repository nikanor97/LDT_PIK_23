import React, {useEffect} from "react";
import {useAppDispatch} from "@root/Hooks";
import Actions from "@actions";
import ProjectsTable from "./Content/ProjectsTable/ProjectsTable";

const Projects = () => {
    const dispatch = useAppDispatch();

    useEffect(() => {
        dispatch(Actions.Projects.getProjects());
    }, []);

    return (
        <div>
            <ProjectsTable />
        </div>
    );
};

export default Projects;
