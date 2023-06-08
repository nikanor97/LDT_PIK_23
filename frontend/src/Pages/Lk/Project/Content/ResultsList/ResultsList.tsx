import Title from "@root/Components/Title/Title";
import {useAppDispatch, useAppSelector} from "@root/Hooks";
import React, {useEffect} from "react";
import styles from "./ResultsList.module.less";
import {Tag} from "antd";
import Actions from "@actions";
import routes from "@root/Routes/Routes";
import {useHistory} from "react-router-dom";
import BackArrow from "@root/Assets/Icons/BackArrow/BackArrow";

const ResultList = () => {
    const selectedProject = useAppSelector((state) => state.Projects.selectedProject);
    const resultOptions = useAppSelector((state) => state.Projects.selectedProject?.results);
    const dispatch = useAppDispatch();
    const history = useHistory();

    if (!selectedProject) return null;
    if (!resultOptions) return null;

    return (
        <div className={styles.wrapper}>
            <div className={styles.backCol}
                onClick={() => history.push(routes.lk.projects)}>
                <BackArrow /> К проектам
            </div>
            <div className={styles.header}>
                <Title variant="h1" className={styles.title}>
                    {selectedProject.name}
                </Title>
                <Tag className={styles.tagSuccess}>Готово</Tag>
            </div>

            <div className={styles.block}>
                <div className={styles.blockHeader}>
                    Результаты расчётов
                </div>
                <div className={styles.blockContent}>
                    {resultOptions.map((item, index) => (
                        <div
                            key={item.variant_num}
                            onClick={() => dispatch(Actions.Projects.setSelectedOption(item))}
                            className={styles.blockContentOption}>
                            <div className={styles.blockContentOptionTop}>
                                <div className={styles.blockContentOptionTopIcon}>
                                    {item.variant_num}
                                </div>
                                <div className={styles.blockContentOptionTopTitle}>
                                    Расчёт №{item.variant_num}
                                </div>
                            </div>

                            <div className={styles.blockContentOptionInfo}>
                                <div className={styles.blockContentOptionInfoDesc}>
                                    Количество фитингов:
                                </div>
                                <div className={styles.blockContentOptionInfoNum}>
                                    {item.n_fittings}
                                </div>
                            </div>
                            <div className={styles.blockContentOptionInfo}>
                                <div className={styles.blockContentOptionInfoDesc}>
                                    Общая длина канализации:
                                </div>
                                <div className={styles.blockContentOptionInfoNum}>
                                    {item.sewer_length}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>

    );
};

export default ResultList;
