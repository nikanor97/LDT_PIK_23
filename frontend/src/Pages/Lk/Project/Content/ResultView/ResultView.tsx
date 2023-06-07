import React, {useEffect} from "react";
import MaterialTab from "./Tabs/MaterialTab/MaterialTab";
import ConnectPointsTab from "./Tabs/ConnectPointsTab/ConnectPointsTab";
import GraphTab from "./Tabs/GraphTab/GraphTab";
import {useAppDispatch, useAppSelector} from "@root/Hooks";
import {Dropdown, Tabs} from "antd";
import Icon from "@ant-design/icons/lib/components/Icon";
import Back from "./Icons/Back";
import Actions from "@actions";
import {Button} from "@root/Components/Controls";
import {useHistory, useParams} from "react-router-dom";
import DownloadMenu from "./Modules/DownloadMenu/DownloadMenu";
import routes from "@root/Routes/Routes";
import styles from "./ResultView.module.less";

const {TabPane} = Tabs;

type iParams = {
    projectID: string
}

const ResultView = () => {
    const option = useAppSelector((state) => state.Projects.selectedOption);
    const file = useAppSelector((state) => state.Projects.file);
    const dispatch = useAppDispatch();
    const {projectID} = useParams<iParams>();
    const history = useHistory();
    
    if (!option) return null;

    useEffect(() => {
        if (!file) {
            dispatch(Actions.Projects.downloadFile({
                project_id: projectID,
                variant_num: option.variant_num,
                file_type: "stl"
            }));
        }
        return () => {
            dispatch(Actions.Projects.setSelectedOption(null));
            dispatch(Actions.Projects.eraseFile());
        };
    }, []);

    return (
        <div className={styles.wrapper}>
            <div className={styles.header}>
                <div className={styles.back}>
                    <Icon component={Back} onClick={() => dispatch(Actions.Projects.setSelectedOption(null))}/>
                    <div className={styles.title}>
                        Расчёт №{option.variant_num}
                    </div>
                </div>
                <Dropdown 
                    trigger={["click"]}
                    overlay={<DownloadMenu project={projectID} variant={option.variant_num}/>}>
                    <Button 
                        type="primary">
                        Экспорт
                    </Button>
                </Dropdown>
            </div>
            <Tabs defaultActiveKey="2" >
                {/* <TabPane tab={option.materials.tabName} key="1">
                    <MaterialTab tables={option.materials.tables} />
                </TabPane> */}
                <TabPane tab={option.result.connection_points.tab_name} key="2">
                    <ConnectPointsTab data={option.result.connection_points} />
                </TabPane>
                <TabPane tab={option.result.graph.tab_name} key="3">
                    <GraphTab data={option.result.graph} />
                </TabPane>
            </Tabs>
        </div>
    );
};

export default ResultView;
