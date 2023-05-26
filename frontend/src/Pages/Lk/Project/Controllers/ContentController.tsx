import React from "react";
import {useAppSelector} from "@root/Hooks";
import Loading from "@root/Components/Loading/Loading";
import {Empty} from "antd";
import EmptyImage from "@root/Assets/Icons/EmptyImage/EmptyImage";
import ResultList from "../Content/ResultsList/ResultsList";
import ResultView from "../Content/ResultView/ResultView";

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
        if (selectedProject.resultOptions) {
            console.log(selectedOption);
            if (selectedOption !== null) {
                
                return <ResultView />;
            } else {
                return (<ResultList />);
            }

        } else {
            return (
                <Empty
                    imageStyle={{height: "200px",
                        width: "200px",
                        margin: "auto"}}
                    image={<EmptyImage />}
                    style={{margin: "auto"}}
                    description="Информация о проекте не загрузилась"/>);
        }
    }
    if (!selectedProject) return (
        <Empty
            imageStyle={{height: "200px",
                width: "200px",
                margin: "auto"}}
            image={<EmptyImage />}
            style={{margin: "auto"}}
            description="Информация о проекте не загрузилась"/>);
    return null;
};

export default ContentController;
