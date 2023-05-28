import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import Api from "@api";
import Cookies from "universal-cookie";

const cookies = new Cookies();

const UserInfo = function* () {
    try {
        const {data} = yield call(Api.User.getUserInfo);
        yield put(Actions.User._getUserInfoSuccess({
            ...data,
            auth: true
        }));
    } catch (error) {
        yield put(Actions.User._getUserInfoError({auth: false}));
        cookies.remove("refresh", {path: "/"});
    } finally {
        yield put(Actions.User.setFetching(false));
    }
};

export default function* () {
    yield takeLatest(Actions.User.getUserInfo, UserInfo);
}
