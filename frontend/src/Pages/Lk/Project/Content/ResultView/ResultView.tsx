import {useAppDispatch, useAppSelector} from "@root/Hooks";
import React from "react";
import MaterialTab from "./Tabs/MaterialTab/MaterialTab";
import ConnectPointsTab from "./Tabs/ConnectPointsTab/ConnectPointsTab";
import GraphTab from "./Tabs/GraphTab/GraphTab";
import styles from "./ResultView.module.less";

import {Tabs} from "antd";
import Icon from "@ant-design/icons/lib/components/Icon";
import Back from "./Icons/Back";
import Actions from "@actions";

const {TabPane} = Tabs;

const ResultView = () => {
    const selectedOption = useAppSelector((state) => state.Projects.selectedOption);
    if (selectedOption === null) return null;
    const option = useAppSelector((state) => state.Projects.selectedProject!.resultOptions![selectedOption]);
    const dispatch = useAppDispatch();

    return (
        <div className={styles.wrapper}>
            <div className={styles.header}>
                <Icon component={Back} onClick={() => dispatch(Actions.Projects.setSelectedOption(null))}/>
                <div  className={styles.title}>
                    Вариант {selectedOption + 1}
                </div>
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
