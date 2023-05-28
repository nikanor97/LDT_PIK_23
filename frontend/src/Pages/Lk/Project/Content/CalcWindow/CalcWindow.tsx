import Title from "@root/Components/Title/Title";
import React from "react";
import styles from "./CalcWindow.module.less";
import {useAppDispatch, useAppSelector} from "@root/Hooks";
import {Tag} from "antd";
import DXF from "./Modules/DXF/DXF";
import Manual from "./Modules/Manual/Manual";
import routes from "@root/Routes/Routes";
import {useHistory} from "react-router-dom";
import BackArrow from "@root/Assets/Icons/BackArrow/BackArrow";

const CalcWindow = () => {
    const selectedProject = useAppSelector((state) => state.Projects.selectedProject);
    const dispatch = useAppDispatch();
    const history = useHistory();

    if (!selectedProject) return null;

    const calcType = selectedProject.type;

    return (
        <div className={styles.wrapper}>
            <div className={styles.backCol}
                onClick={() => history.push(routes.lk.projects)}>
                <BackArrow /> Проекты
            </div>
            <div className={styles.header}>
                <Title variant="h1" className={styles.title}>
                    {selectedProject.name}
                </Title>
                <Tag className={styles.tagProcess}>В процессе</Tag>
            </div>

            <div className={styles.block}>
                <div className={styles.blockHeader}>
                    Введите данные для расчёта
                </div>
                <div className={styles.blockContent}>
                    {calcType === "dxf" ? (
                        <DXF />
                    ) : (
                        <Manual />
                    )}
                </div>
            </div>
        </div>
    );
};

export default CalcWindow;
