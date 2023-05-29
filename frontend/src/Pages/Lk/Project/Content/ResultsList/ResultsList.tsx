import Title from "@root/Components/Title/Title";
import {useAppDispatch, useAppSelector} from "@root/Hooks";
import React from "react";
import styles from "./ResultsList.module.less";
import {Tag} from "antd";
import Actions from "@actions";
import routes from "@root/Routes/Routes";
import {useHistory} from "react-router-dom";
import BackArrow from "@root/Assets/Icons/BackArrow/BackArrow";

const ResultList = () => {
    const selectedProject = useAppSelector((state) => state.Projects.selectedProject);
    const resultOptions = useAppSelector((state) => state.Projects.selectedProject?.result);
    const dispatch = useAppDispatch();
    const history = useHistory();

    if (!selectedProject) return null;
    if (!resultOptions) return null;

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
                <Tag className={styles.tagSuccess}>Готово</Tag>
            </div>

            <div className={styles.block}>
                <div className={styles.blockHeader}>
                    Результаты расчета
                </div>
                <div className={styles.blockContent}>
                    {/* {resultOptions.map((item, index) => (
                        <div key={index + 1} onClick={() => dispatch(Actions.Projects.setSelectedOption(index))} className={styles.blockContentOption}>
                            <div className={styles.blockContentOptionTitle}>
                                Вариант {index + 1}
                            </div>
                        </div>
                    ))} */}
                </div>
            </div>
        </div>

    );
};

export default ResultList;
