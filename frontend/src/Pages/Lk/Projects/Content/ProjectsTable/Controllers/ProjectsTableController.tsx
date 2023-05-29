import React from "react";
import {useAppSelector} from "@root/Hooks";
import {Empty} from "antd";
import TableView from "../Views/TableView/TableView";
import EmptyItem from "../Views/EmptyItem/EmptyItem";
import Loading from "@root/Components/Loading/Loading";
import EmptyDocuments from "@root/Assets/Icons/EmptyDocuments/EmptyDocuments";

const ProjectsTableController = () => {
    const projects = useAppSelector((state) => state.Projects.projects);
    const getProjectsFetching = useAppSelector((state) => state.Projects.getFetching);

    if (getProjectsFetching) return <Loading />;
    if (projects && projects.length > 0) return (<TableView />);
    if (!projects) return <EmptyItem />;
    if (!projects || projects.length === 0) return (
        <Empty
            imageStyle={{height: "200px",
                width: "200px",
                margin: "auto",
                marginTop: "32px"}}
            image={<EmptyDocuments />} 
            description="Отсутствуют созданные проекты"
        />
    );
    return null;
};

export default ProjectsTableController;
