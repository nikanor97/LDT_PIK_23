import React from "react";
import StatCard from "./Components/StatCard/StatCard";
import styles from "./StatBar.module.less";

const StatBar = () => {
    const mockStat = [
        {
            title: "Всего фитингов",
            value: 100
        },
        {
            title: "Средняя длина канализации",
            value: 356.32
        },
        {
            title: "Среднее количество устройств",
            value: 210
        }
    ];

    return (
        <div className={styles.wrapper}>
            {mockStat.map((item) => (
                <StatCard
                    className={styles.card}
                    key={item.title}
                    title={item.title}
                    value={item.value}
                />
            ))}
        </div>
    );
};

export default StatBar;
