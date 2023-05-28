import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import Api from "@api";
import base64 from "@root/Pages/Lk/Projects/Content/TopBar/Modules/CreateProject/Modules/CreateProjectModal/base64";

const GetFittingsGroup = function* () {
    try {
        const {data} = yield call(Api.Projects.getFittingsGroup);
        yield put(Actions.Projects._getFittingsSuccess(data));
    } catch (error) {
        yield put(Actions.Projects._getFittingsError());
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.getFittings, GetFittingsGroup);
}
