import React from "react";
import {takeEvery, call, put} from "redux-saga/effects";
import Actions from "@actions";
import {PayloadAction} from "@reduxjs/toolkit";
import Api from "@api";
import {iActions} from "@redux/Auth/types";
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
        yield call(
            {
                context: cookies,
                fn: cookies.set,
            },
            "access",
            data.access_token,
            {
                expires: new Date(data.access_expires_at * 1000),
                path: "/",
            }
        );
        yield call(
            {
                context: cookies,
                fn: cookies.set,
            },
            "refresh",
            data.refresh_token,
            {
                expires: new Date(data.refresh_expires_at * 1000),
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
