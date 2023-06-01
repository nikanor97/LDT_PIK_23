import React from "react";
import {useAppDispatch, useAppSelector} from "@root/Hooks";
import Actions from "@actions";
import styles from "./DownloadMenu.module.less";
import {Button} from "@components/Controls";

type DownloadMenuProps = {
    project: string,
    variant: number
}

const MenuModule = (props: DownloadMenuProps) => {
    const loading = useAppSelector((state) => state.Projects.loadingDownload);
    const dispatch = useAppDispatch();
    const {project, variant} = props;

    const onDownloadStl = () => {
        dispatch(Actions.Projects.downloadResult({
            project_id: project,
            variant_num: 0,
            file_type: "stl"
        }));
    };

    const onDownloadXls = () => {
        dispatch(Actions.Projects.downloadResult({
            project_id: project,
            variant_num: 0,
            file_type: "csv"
        }));
    };
    return (
        <div className={styles.wrapper}>
            <Button
                type="menu"
                className={styles.btn}
                loading={loading}
                onClick={onDownloadStl}>
                STL
            </Button>
            <Button
                type="menu"
                className={styles.btn}
                loading={loading}
                onClick={onDownloadXls}>
                CSV
            </Button>
        </div>
    );
};

export default MenuModule;
