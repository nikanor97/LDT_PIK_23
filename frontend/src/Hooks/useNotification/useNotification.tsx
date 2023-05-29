import React from "react";
import {notification} from "antd";
import {NotificationPlacement} from "antd/lib/notification";
import Info from "./Icons/Info";
import Close from "./Icons/Close";
import Error from "./Icons/Error";

const placement: NotificationPlacement = "bottomLeft";
const duration: number = 4;

const closeIcon: React.ReactNode = <Close />; 
const infoIcon: React.ReactNode = <Info />;
const errorIcon: React.ReactNode = <Error />;

const notificationConfig = {
    placement,
    closeIcon,
    duration,
    icons: {
        info: infoIcon,
        error: errorIcon,
    },
    
};

type notificationProps = {
    type: "info" | "error",
    message: string,
    duration?: number,
};

const useNotification = () => {
    return (props: notificationProps) => {
        const {message, type, duration} = props;
        const icon = type === "info" 
            ? notificationConfig.icons.info
            : notificationConfig.icons.error;
            
        notification[type]({
            message,
            icon,
            duration: duration ? duration : notificationConfig.duration,
            placement: notificationConfig.placement,
            closeIcon: notificationConfig.closeIcon,
        });
    };
};

export default useNotification;
