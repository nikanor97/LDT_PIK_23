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
import {useHistory, useParams} from "react-router-dom";
import DownloadMenu from "./Modules/DownloadMenu/DownloadMenu";
import routes from "@root/Routes/Routes";

const {TabPane} = Tabs;

type iParams = {
    projectID: string
}

const ResultView = () => {
    // const selectedOption = useAppSelector((state) => state.Projects.selectedOption);
    // if (selectedOption === null) return null;
    const option = useAppSelector((state) => state.Projects.selectedProject?.result);
    const dispatch = useAppDispatch();
    const {projectID} = useParams<iParams>();
    const history = useHistory();

    console.log(option);
    if (!option) return null;

    useEffect(() => {
        return () => {
            dispatch(Actions.Projects.setSelectedOption(null));
        };
    });

    return (
        <div className={styles.wrapper}>
            <div className={styles.header}>
                <div className={styles.back}>
                    <Icon component={Back} onClick={() => history.push(routes.lk.projects)}/>
                    {/* <div  className={styles.title}>
                    Вариант {selectedOption + 1}
                    </div> */}
                </div>
                {/* <Dropdown 
                    trigger={["click"]}
                    overlay={<DownloadMenu project={projectID} variant={1}/>}>
                    <Button 
                        type="primary">
                        Экспорт
                    </Button>
                </Dropdown> */}
            </div>
            <Tabs defaultActiveKey="2">
                {/* <TabPane tab={option.materials.tabName} key="1">
                    <MaterialTab tables={option.materials.tables} />
                </TabPane> */}
                <TabPane tab={option.connection_points.tab_name} key="2">
                    <ConnectPointsTab data={option.connection_points} />
                </TabPane>
                <TabPane tab={option.graph.tab_name} key="3">
                    <GraphTab data={option.graph} />
                </TabPane>
            </Tabs>
        </div>
    );
};

export default ResultView;
