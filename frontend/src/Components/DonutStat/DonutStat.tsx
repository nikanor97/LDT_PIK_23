import React from "react";
import {VictoryPie, VictoryContainer, VictoryTooltip} from "victory";
import Tooltip from "../Tooltip/Tooltip";
import styles from "./DonutStat.module.less";

export type ChartDonutData = {
    x: string,
    y: number,
    fill: string
}[]

type DonutStatProps = {
    stat: ChartDonutData;
    sum: number;
    title: string;
}

const DonutStat = (props: DonutStatProps) => {
    return (
        <div className={styles.pieStat}>
            <div className={styles.title}>
                {props.title}
            </div>
            {props.sum === 0 ? (
                <div className={styles.pie}>
                    <VictoryPie
                        innerRadius={25}
                        cornerRadius={4}
                        padAngle={2}
                        height={120}
                        width={120}
                        padding={{top: 0,
                            bottom: 0,
                            right: 16,
                            left: 0}}
                        containerComponent={<VictoryContainer responsive={false}/>}
                        style={{
                            data: {
                                fill: ({datum}) => datum.fill
                            }
                        }}
                        data={[
                            {
                                x: 1,
                                y: 1,
                                fill: "rgb(238, 239, 238)",
                            }
                        ]}/>
                    <div className={styles.pieInfo}>
                        <div className={styles.pieInfoEmptyText}>
                            Сможем посчитать все девайсы, когда вы создадите расчёт в проекте
                        </div>
                    </div>
                </div>
            ) : (
                <div className={styles.pie}>
                    <VictoryPie
                        innerRadius={25}
                        cornerRadius={4}
                        padAngle={2}
                        height={120}
                        width={120}
                        padding={{top: 0,
                            bottom: 0,
                            right: 16,
                            left: 0}}
                        labels={({datum}) => `${Math.round(datum.y / props.sum * 100)}%`}
                        containerComponent={<VictoryContainer responsive={false}/>}
                        labelComponent={<VictoryTooltip
                            style={{
                                fontFamily: "Inter",
                                fontWeight: 700,
                            }}
                            flyoutStyle={{
                                stroke: "var(--donut-tooltip-border)",
                                fill: "var(--donut-tooltip-bg)"
                            }}
                        />}
                    
                        style={{
                            data: {
                                fill: ({datum}) => datum.fill
                            }
                        }}
                        data={props.stat}/>
                    <div className={styles.pieInfo}>
                        {props.stat.map((item, index) => (
                            <div
                                className={styles.subInfo}
                                key={index}>
                                <div className={styles.name}>
                                    <span style={{
                                        height: "8px",
                                        width: "8px",
                                        backgroundColor: item.fill,
                                        borderRadius: "50%",
                                        display: "inline-block",
                                        marginRight: "8px"
                                    }}/>
                                    {item.x}
                                </div>
                                <div className={styles.count}>
                                    {item.y}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

        </div>
    );
};

export default DonutStat;
