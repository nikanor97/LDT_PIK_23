import React from "react";
import ContentController from "./Controllers/ContentController";
import styles from "./Auth.module.less";

const AuthPage = () => {
    return (
        <div className={styles.wrapper}>
            <div className={styles.content}>
                <ContentController />
            </div>
        </div>
    );
};

export default AuthPage;
