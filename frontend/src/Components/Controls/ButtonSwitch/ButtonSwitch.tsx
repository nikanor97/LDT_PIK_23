import {Space, Radio, RadioChangeEvent} from "antd";
import React from "react";
import styles from "./ButtonSwitch.module.less";

export type ButtonSwitchProps = {
    onChange: (e: RadioChangeEvent) => void;
    rightItem: ButtonSwitchItem;
    leftItem: ButtonSwitchItem;
    defaultValue: string | number
    // TODO по умолчаю dValue : any => необходимо дописывать типы при расширении чтобы не писать any
}

type ButtonSwitchItem = {
    value: string;
    title: string;
}

const ButtonSwitch = (props: ButtonSwitchProps) => {
    return (
        <Space
            className={styles.wrapper}>
            <Radio.Group
                buttonStyle="solid"
                defaultValue={props.defaultValue}
                onChange={(event) => {
                    props.onChange(event);
                }}>
                <Radio.Button value={props.leftItem.value}>
                    {props.leftItem.title}
                </Radio.Button>
                <Radio.Button value={props.rightItem.value}>
                    {props.rightItem.title}
                </Radio.Button>
            </Radio.Group>
        </Space>
    );
};

export default ButtonSwitch;
