import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import Api from "@api";

const GetUsersAll = function* () {
    const data = [
        {
            user_id: "asdfasdf45235",
            name: "Пупкин В.С."
        },
        {
            user_id: "asdfasdfgher23414",
            name: "Лупкин Г.В."
        }
    ];

    try {
        // const {data} = yield call(Api.User.getUsersAll);
        yield put(Actions.User._getUserAllSuccess(data));
    } catch (error) {
        yield put(Actions.User._getUserAllError());
    }
};

export default function* () {
    yield takeLatest(Actions.User.getUsersAll, GetUsersAll);
}
