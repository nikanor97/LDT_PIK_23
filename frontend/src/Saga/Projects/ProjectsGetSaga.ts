import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import Api from "@api";
import useNotification from "@root/Hooks/useNotification/useNotification";
import {iApi} from "@root/types";

const GetProjects = function* () {
    const notification = useNotification();

    try {
        const {data} = yield call(Api.Projects.getProjects);
        yield put(Actions.Projects._getProjectsSuccess(data));
    } catch (error) {
        yield put(Actions.Projects._getProjectsError());
        notification({
            type: "error",
            message: "При загрузке проектов произошла ошибка"
        });
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.getProjects, GetProjects);
}
