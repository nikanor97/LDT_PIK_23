import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import Api from "@api";
import useNotification from "@root/Hooks/useNotification/useNotification";
import {iApi} from "@root/types";

const GetProjects = function* () {
    const notification = useNotification();

    const mockData: iApi.Projects.Item[] = [
        {
            id: 1,
            name: "Project 1",
            bathroomType: "Type 1",
            author: "Пупкин В.С.",
            status: 200,
            performer: "Лупкин Г.В."
        },
        {
            id: 2,
            name: "Project 2",
            bathroomType: "Type 2",
            author: "Пупкин В.С.",
            status: 100,
            performer: "Лупкин Г.В."
        },
        {
            id: 3,
            name: "Project 3",
            bathroomType: "Type 3",
            author: "Пупкин В.С.",
            status: 400,
            performer: "Лупкин Г.В."
        },
        {
            id: 4,
            name: "Project 4",
            bathroomType: "Type 2",
            author: "Пупкин В.С.",
            status: 200,
            performer: "Лупкин Г.В."
        },
    ];

    try {
        // const {data} = yield call(Api.Projects.getProjects);
        yield put(Actions.Projects._getProjectsSuccess(mockData));
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
