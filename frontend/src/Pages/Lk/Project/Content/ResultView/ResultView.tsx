import {useAppDispatch, useAppSelector} from "@root/Hooks";
import React, {useEffect} from "react";
import MaterialTab from "./Tabs/MaterialTab/MaterialTab";
import ConnectPointsTab from "./Tabs/ConnectPointsTab/ConnectPointsTab";
import GraphTab from "./Tabs/GraphTab/GraphTab";
import styles from "./ResultView.module.less";

import {Dropdown, Tabs} from "antd";
import Icon from "@ant-design/icons/lib/components/Icon";
import Back from "./Icons/Back";
import Actions from "@actions";
import {Button} from "@root/Components/Controls";
import {useParams} from "react-router-dom";
import DownloadMenu from "./Modules/DownloadMenu/DownloadMenu";

const {TabPane} = Tabs;

type iParams = {
    projectID: string
}

const ResultView = () => {
    const selectedOption = useAppSelector((state) => state.Projects.selectedOption);
    if (selectedOption === null) return null;
    const option = useAppSelector((state) => state.Projects.selectedProject!.resultOptions![selectedOption]);
    const dispatch = useAppDispatch();
    const {projectID} = useParams<iParams>();

    useEffect(() => {
        return () => {
            dispatch(Actions.Projects.setSelectedOption(null));
        };
    });

    return (
        <div className={styles.wrapper}>
            <div className={styles.header}>
                <div className={styles.back}>
                    <Icon component={Back} onClick={() => dispatch(Actions.Projects.setSelectedOption(null))}/>
                    <div  className={styles.title}>
                    Вариант {selectedOption + 1}
                    </div>
                </div>
                <Dropdown 
                    trigger={["click"]}
                    overlay={<DownloadMenu project={projectID} variant={selectedOption}/>}>
                    <Button 
                        type="primary">
                        Экспорт
                    </Button>
                </Dropdown>
            </div>
            <Tabs defaultActiveKey="1">
                <TabPane tab={option.materials.tabName} key="1">
                    <MaterialTab tables={option.materials.tables} />
                </TabPane>
                <TabPane tab={option.connectionPoints.tabName} key="2">
                    <ConnectPointsTab data={option.connectionPoints} />
                </TabPane>
                <TabPane tab={option.graph.tabName} key="3">
                    <GraphTab data={option.graph} />
                </TabPane>
            </Tabs>
        </div>
    );
};

export default ResultView;
