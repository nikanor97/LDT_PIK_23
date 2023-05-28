import React, {useEffect} from "react";
import Actions from "@actions";
import {useAppDispatch, useAppSelector} from "@root/Hooks";
import {Layout} from "antd";
import Loading from "@components/Loading/Loading";

interface iCheckUserContainerProps {
    children: JSX.Element
}

const CheckUserContainer = (props: iCheckUserContainerProps) => {
    const {children} = props;
    const dispatch = useAppDispatch();
    const fetching = useAppSelector((state) => state.User.fetching);

    useEffect(() => {
        dispatch(Actions.User.getUserInfo());
    }, []);

    if (fetching) {
        return (
            <Layout style={{
                height: "100vh",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                background: "#23252B"
            }}>
                <Loading>
                    Загрузка...
                </Loading>
            </Layout>
        );
    }

    return (
        <>
            {children}
        </>
    );
};

export default CheckUserContainer;
