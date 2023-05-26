import Title from "@root/Components/Title/Title";
import {useAppDispatch, useAppSelector} from "@root/Hooks";
import React from "react";
import styles from "./ResultsList.module.less";
import {Tag} from "antd";
import Actions from "@actions";

const ResultList = () => {
    const selectedProject = useAppSelector((state) => state.Projects.selectedProject);
    const resultOptions = useAppSelector((state) => state.Projects.selectedProject?.resultOptions);
    const dispatch = useAppDispatch();

    if (!selectedProject) return null;
    if (!resultOptions) return null;

    return (
        <div className={styles.wrapper}>
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
                    {resultOptions.map((item, index) => (
                        <div key={index + 1} onClick={() => dispatch(Actions.Projects.setSelectedOption(index))} className={styles.blockContentOption}>
                            <div className={styles.blockContentOptionTitle}>
                                Вариант {index + 1}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>

    );
};

export default ResultList;
