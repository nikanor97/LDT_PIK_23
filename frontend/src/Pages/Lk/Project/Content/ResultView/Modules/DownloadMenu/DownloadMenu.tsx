import React from "react";
import {useAppDispatch} from "@root/Hooks";
import Actions from "@actions";
import styles from "./DownloadMenu.module.less";
import {Button} from "@components/Controls";

type DownloadMenuProps = {
    project: string,
    variant: number
}

const MenuModule = (props: DownloadMenuProps) => {
    const dispatch = useAppDispatch();
    const {project, variant} = props;

    const onDownloadStl = () => {
        dispatch(Actions.Projects.downloadResult({
            project,
            variant,
            file_type: "stl"
        }));
    };

    const onDownloadXls = () => {
        dispatch(Actions.Projects.downloadResult({
            project,
            variant,
            file_type: "xls"
        }));
    };
    return (
        <div className={styles.wrapper}>
            <Button
                type="menu"
                className={styles.btn}
                onClick={onDownloadStl}>
                STL
            </Button>
            <Button
                type="menu"
                className={styles.btn}
                onClick={onDownloadXls}>
                XLS
            </Button>
        </div>
    );
};

export default MenuModule;
