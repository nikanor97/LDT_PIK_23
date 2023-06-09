import React from "react";
import styles from "./StatBar.module.less";
import useStatisticsData from "./Hooks/useStatisticsData";
import CountStatBlock from "@root/Components/CountStatBlock/CountStatBlock";
import DonutStat from "@root/Components/DonutStat/DonutStat";
import Fittings from "./Icons/Fittings";
import Sewer from "./Icons/Sewer";

const StatBar = () => {
    const statistics = useStatisticsData();

    if (!statistics) return null;

    return (
        <div className={styles.wrapper}>
            <CountStatBlock
                icon={<Fittings />}
                title={"Среднее количество фитингов"}
                statNumber={statistics.fittings} />
            <CountStatBlock
                icon={<Sewer />}
                title={"Средняя длина канализации"}
                statNumber={statistics.sewer} />
            <DonutStat 
                stat={statistics.device_stat}
                sum={statistics.device_sum}
                title="Количество устройств по типам"
            />

        </div>
    );
};

export default StatBar;
