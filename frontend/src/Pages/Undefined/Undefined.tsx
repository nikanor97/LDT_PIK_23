import React from "react";
import {Button} from "@components/Controls";
import {Link} from "react-router-dom";
import styles from "./Undefined.module.less";
import routes from "@routes";

const UndefinedPage = () => {
    return (
        <div className={styles.wrapper}>
            <div className={styles.content}>
                <div className={styles.title}>
                    Извините, страница не найдена!
                </div>
                <div className={styles.desc}>
                    Вероятнее всего ссылка, по которой вы перешли, больше не является актуальной.
                </div>
                <br/>
                <br />
                <Link
                    className={styles.link}
                    to={"/"}>
                    <Button
                        size="large"
                        color="primary">
                        Перейти домой
                    </Button>
                </Link>
            </div>
        </div>
    );
};

export default UndefinedPage;
