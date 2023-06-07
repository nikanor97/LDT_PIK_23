import React from "react";
import {useAppSelector} from "@root/Hooks";
import Loading from "@root/Components/Loading/Loading";
import {Empty} from "antd";
import ResultList from "../Content/ResultsList/ResultsList";
import ResultView from "../Content/ResultView/ResultView";
import CalcWindow from "../Content/CalcWindow/CalcWindow";
import EmptyDocuments from "@root/Assets/Icons/EmptyDocuments/EmptyDocuments";

const ContentController = () => {
    const selectedProject = useAppSelector((state) => state.Projects.selectedProject);
    const getSelectedProject = useAppSelector((state) => state.Projects.getSelectedProject);
    const selectedOption = useAppSelector((state) => state.Projects.selectedOption);

    if (getSelectedProject) {
        return (
            <Loading>
                Загружаются данные о проекте
            </Loading>
        );
    }
    if (selectedProject) {
        if (selectedProject.status === 0 || selectedProject.status === 400) {
            return (
                <CalcWindow />
            );
        } else {
            return (<ResultView />);
        }
        // if (selectedProject.result) {
        //     // if (selectedOption !== null) {
                
        //     return <ResultView />;
        //     // } else {
        //     //     return (<ResultList />);
        //     // }

        // } else {
        //     return (
        //         <CalcWindow />
        //     );
        // }
    }
    if (!selectedProject) return (
        <Empty
            imageStyle={{height: "200px",
                width: "200px",
                margin: "auto"}}
            image={<EmptyDocuments />}
            style={{margin: "auto"}}
            description="Информация о проекте не загрузилась"/>);
    return null;
};

export default ContentController;
