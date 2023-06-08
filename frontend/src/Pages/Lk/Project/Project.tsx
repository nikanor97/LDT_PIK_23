import {useAppDispatch} from "@root/Hooks";
import React, {useEffect} from "react";
import Actions from "@actions";

import {useParams} from "react-router-dom";
import ContentController from "./Controllers/ContentController";

type iParams = {
    projectID: string
}

const Project = () => {
    const dispatch = useAppDispatch();

    const {projectID} = useParams<iParams>();

    useEffect(() => {
        dispatch(Actions.Projects.getSelectedProject({id: projectID}));

    }, []);

    return (
        <ContentController />
    );
};

export default Project;
