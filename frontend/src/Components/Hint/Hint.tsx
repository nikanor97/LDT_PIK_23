import React from "react";
import styles from "./Hint.module.less";
import Tooltip from "../Tooltip/Tooltip";
import InfoIcon from "./Icons/InfoIcon";
import useGetSize from "./Hooks/useGetSize";
import {RenderFunction} from "antd/lib/tooltip";

type HintProps = {
    title: React.ReactNode | RenderFunction | JSX.Element,
    width?: number,
    height?: number,
};

const Hint = (props: HintProps) => {
    const {width, height} = useGetSize({
        width: props.width,
        height: props.height
    });
    const {title} = props;

    return (
        <Tooltip title={title} placement="right">
            <div
                className={styles.buttonHint}
                style={{
                    width,
                    height
                }}>
                <InfoIcon />
            </div>
        </Tooltip>
    );
};

export default Hint;
