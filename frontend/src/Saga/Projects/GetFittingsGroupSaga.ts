import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import Api from "@api";
import base64 from "@root/Pages/Lk/Projects/Content/TopBar/Modules/CreateProject/Modules/CreateProjectModal/base64";

const GetFittingsGroup = function* () {
    const data = [
        {
            groupName: "Тройники",
            values: [
                {
                    image: base64,
                    name: "Тройник 50х50х45",
                    id: "dlskja22"
                },
                {
                    image: base64,
                    name: "Тройник 50х50х87",
                    id: "qlskjq324"
                },
                {
                    image: base64,
                    name: "Тройник 110х50х87",
                    id: "klfsdlf2"
                },
            ]
        },
        {
            groupName: "Крестовины",
            values: [
                {
                    image: base64,
                    name: "Крестовина 50х50х45",
                    id: "akljsdf2"
                },
                {
                    image: base64,
                    name: "Крестовина 50х50х87",
                    id: "asdfsdf321423"
                },
                {
                    image: base64,
                    name: "Крестовина 110х50х87",
                    id: "asdf222"
                },
            ]
        }
    ];

    try {
        // const {data} = yield call(Api.Projects.getFittingsGroup);
        yield put(Actions.Projects._getFittingsSuccess(data));
    } catch (error) {
        yield put(Actions.Projects._getFittingsError());
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.getFittings, GetFittingsGroup);
}
