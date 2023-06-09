import React, {useEffect} from "react";
import FittingTab from "./Tabs/FittingTab/FittingTab";
import ConnectPointsTab from "./Tabs/ConnectPointsTab/ConnectPointsTab";
import GraphTab from "./Tabs/GraphTab/GraphTab";
import {useAppDispatch, useAppSelector} from "@root/Hooks";
import {Divider, Dropdown, Tabs} from "antd";
import Icon from "@ant-design/icons/lib/components/Icon";
import Back from "./Icons/Back";
import Actions from "@actions";
import {Button} from "@root/Components/Controls";
import {useParams} from "react-router-dom";
import DownloadMenu from "./Modules/DownloadMenu/DownloadMenu";
import styles from "./ResultView.module.less";

const {TabPane} = Tabs;

type iParams = {
    projectID: string
}

const ResultView = () => {
    const option = useAppSelector((state) => state.Projects.selectedOption);
    const selectedProject = useAppSelector((state) => state.Projects.selectedProject);
    const file = useAppSelector((state) => state.Projects.file);
    const dispatch = useAppDispatch();
    const {projectID} = useParams<iParams>();
    
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
                    <Divider className={styles.divider} />
                    <div className={styles.subTitle}>
                        {selectedProject?.name}
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
            <Tabs defaultActiveKey="1" >
                <TabPane tab={option.result.fittings_stat.tab_name} key="1">
                    <FittingTab data={option.result.fittings_stat} />
                </TabPane>
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
