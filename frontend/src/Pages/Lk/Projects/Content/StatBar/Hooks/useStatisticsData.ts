import {useAppSelector} from "@root/Hooks";

export type ChartDonatData = {
    x: string,
    y: number,
    fill: string
}[]

const useStatisticsData = () => {
    const statistics = useAppSelector((state) => state.Projects.statistics);
    if (!statistics) return null;
    const colors = [
        "#9E77ED",
        "#FE9B71",
        "#FEA3B4",
        "#FDB022",
        "#6CE9A6",
        "#55CDFC",
        "#FFD700",
        "#FF5A5F" ];
    const device_stat: ChartDonatData = [];
    let device_sum = 0;

    statistics.devices.forEach((item) => {
        device_sum = device_sum + item.n_occur;
    });

    let counter = 0;

    statistics.devices.forEach((item, index) => {
        if (counter >= colors.length) counter = 0;
        device_stat.push({
            x: item.type_human,
            y: item.n_occur,
            fill: colors[counter]
        });
        counter = counter + 1;
    });

    counter = 0;

    return {
        device_stat,
        device_sum,
        fittings: Math.round(statistics.avg_n_fittings),
        sewer: `${(Math.round(statistics.avg_sewer_length) / 1000).toFixed(2)} м`,
    };
};

export default useStatisticsData;
