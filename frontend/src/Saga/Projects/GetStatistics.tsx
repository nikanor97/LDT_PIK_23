import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import Api from "@api";
import React from "react";
import useNotification from "@root/Hooks/useNotification/useNotification";

const getStatistics = function* () {
    const notification = useNotification();

    try {
        const {data} = yield call(Api.Projects.getProjectStatistic);
        yield put(Actions.Projects._getStatisticsSuccess(data));
    } catch (error) {
        yield put(Actions.Projects._getStatisticsError());
        notification({
            type: "error",
            message: "При загрузке статистики произошла ошибка"
        });
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.getStatistics, getStatistics);
}
