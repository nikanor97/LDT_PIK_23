import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import Api from "@api";

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
