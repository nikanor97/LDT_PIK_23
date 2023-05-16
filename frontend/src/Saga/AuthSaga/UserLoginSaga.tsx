import React from "react";
import {takeEvery, call, put} from "redux-saga/effects";
import Actions from "@actions";
import {PayloadAction} from "@reduxjs/toolkit";
import Api from "@api";
import {iActions} from "@redux/Auth/types";
import {decode, jwtToken} from "@utils/JWT/decode";
import Cookies from "universal-cookie";
import useNotification from "@root/Hooks/useNotification/useNotification";

const cookies = new Cookies();

const UserLogin = function* (action: PayloadAction<iActions.userLogin>) {
    const {payload} = action;
    const notification = useNotification();

    try {
        const {data} = yield call(Api.Auth.login, payload);
        if (!data) throw new Error("Ошибка авторизации");
        yield put(Actions.User.setFetching(true));
        const decodedAccess: jwtToken = decode(data.access);
        yield call(
            {
                context: cookies,
                fn: cookies.set,
            },
            "access",
            data.access,
            {
                // TODO Пока нет SSL сертификата, убираю это
                // secure: true,
                expires: new Date(decodedAccess.exp * 1000),
                path: "/",
            }
        );
        const decodedRefresh: jwtToken = decode(data.refresh);
        yield call(
            {
                context: cookies,
                fn: cookies.set,
            },
            "refresh",
            data.refresh,
            {
                // TODO Пока нет SSL сертификата, убираю это
                // secure: true,
                expires: new Date(decodedRefresh.exp * 1000),
                path: "/",
            }
        );
        yield put(Actions.User.getUserInfo());
        yield put(Actions.Auth._userLoginSuccess());
        action.payload.redirect();
    } catch (error: any) {
        action.payload.setFieldsErrors(error.response.data);
        yield put(Actions.Auth._userLoginError());
        notification({
            type: "error",
            message: "При логине произошла ошибка"
        });
    }
};

export default function* () {
    yield takeEvery(Actions.Auth.userLogin, UserLogin);
}
