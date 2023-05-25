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
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 2,
            name: "Project 2",
            bathroomType: "Type 2",
            author: "Пупкин В.С.",
            status: 100,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 3,
            name: "Project 3",
            bathroomType: "Type 3",
            author: "Пупкин В.С.",
            status: 400,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 4,
            name: "Project 4",
            bathroomType: "Type 2",
            author: "Пупкин В.С.",
            status: 200,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 5,
            name: "Project 5",
            bathroomType: "Type 1",
            author: "Пупкин В.С.",
            status: 200,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 6,
            name: "Project 6",
            bathroomType: "Type 2",
            author: "Пупкин В.С.",
            status: 100,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 7,
            name: "Project 7",
            bathroomType: "Type 3",
            author: "Пупкин В.С.",
            status: 400,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 8,
            name: "Project 8",
            bathroomType: "Type 2",
            author: "Пупкин В.С.",
            status: 200,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 9,
            name: "Project 9",
            bathroomType: "Type 1",
            author: "Пупкин В.С.",
            status: 200,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 10,
            name: "Project 10",
            bathroomType: "Type 2",
            author: "Пупкин В.С.",
            status: 100,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 11,
            name: "Project 11",
            bathroomType: "Type 3",
            author: "Пупкин В.С.",
            status: 400,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 12,
            name: "Project 12",
            bathroomType: "Type 2",
            author: "Пупкин В.С.",
            status: 200,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 13,
            name: "Project 13",
            bathroomType: "Type 1",
            author: "Пупкин В.С.",
            status: 200,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 14,
            name: "Project 14",
            bathroomType: "Type 2",
            author: "Пупкин В.С.",
            status: 100,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 15,
            name: "Project 15",
            bathroomType: "Type 3",
            author: "Пупкин В.С.",
            status: 400,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
        {
            id: 16,
            name: "Project 16",
            bathroomType: "Type 2",
            author: "Пупкин В.С.",
            status: 200,
            performer: "Лупкин Г.В.",
            type: "DXF"
        },
    ];

    try {

        //TODO Убрать Моки

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
