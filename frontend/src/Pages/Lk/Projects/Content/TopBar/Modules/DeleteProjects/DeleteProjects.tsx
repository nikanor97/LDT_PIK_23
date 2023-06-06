import React, {useEffect, useState} from "react";
import  {
    useGetValidNoun,
    useAppDispatch,
    useAppSelector
} from "@root/Hooks";
import Actions from "@actions";
import {Popconfirm} from "antd";
import styles from "./DeleteProjects.module.less";
import useNotification from "@root/Hooks/useNotification/useNotification";
import Tooltip from "@root/Components/Tooltip/Tooltip";
import {Button} from "@root/Components/Controls";
import {DeleteOutlined} from "@ant-design/icons";

const DeleteProjects = () => {
    
    const selectedProjects = useAppSelector((state) => state.Projects.selectedProjects);
    const dispatch = useAppDispatch();
    const notification = useNotification();
    const nounTypes = {
        type1: "проект",
        type2: "проекта",
        type3: "проектов",
    };

    const nounTotalTypes = {
        type1: "Выбран",
        type2: "Выбрано",
        type3: "Выбраны",
    };

    const onDeleteDocuments = () => {
        if (selectedProjects) {
            dispatch(Actions.Projects.deleteProjects(selectedProjects));
        }
    };

    const onCancelDeleteDocuments = () => {
        notification({
            type: "info",
            message: "Удаление отменено"
        });
    };

    if (!selectedProjects) return null;

    return (
        selectedProjects && selectedProjects.length > 0 ? (
            <div className={styles.wrapper}>
                <div className={styles.total}>
                    {useGetValidNoun({
                        nounTypes: nounTotalTypes,
                        number: selectedProjects.length,
                    })} {selectedProjects.length} {useGetValidNoun({
                        nounTypes,
                        number: selectedProjects.length,
                    })}
                </div>
                <Tooltip className={styles.deleteButton}
                    title="Удалить">
                    <Popconfirm
                        title="Вы уверены, что хотите удалить эти проекты?"
                        onConfirm={() => onDeleteDocuments()}
                        onCancel={() => onCancelDeleteDocuments()}
                        okText="Да"
                        cancelText="Нет"
                        placement="bottomLeft"
                    >
                        <span>
                            <Button
                                className={styles.button}
                                type="stroke"
                                size="middle"
                                icon={<DeleteOutlined />}>
                                Удалить
                            </Button>
                        </span>
                    </Popconfirm>     
                </Tooltip>
            </div>

        ) : (
            null
        )
    );
};

export default DeleteProjects;
