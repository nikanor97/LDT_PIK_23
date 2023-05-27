import {takeLatest, call, put} from "redux-saga/effects";
import Actions from "@actions";
import {PayloadAction} from "@reduxjs/toolkit";
import Api from "@api";
import {iActions} from "@redux/Projects/types";
import React from "react";
import useNotification from "@root/Hooks/useNotification/useNotification";
import {iApi} from "@root/types";
import base64 from "@root/Pages/Lk/Projects/Content/TopBar/Modules/CreateProject/Modules/CreateProjectModal/base64";

const getSelectedProject = function* (action: PayloadAction<iActions.getSelectedProject>) {
    const {payload} = action;
    const notification = useNotification();

    const data: iApi.Projects.ItemDetail = {
        id: 1,
        name: "ЖК У Тракториста",
        bathroomType: "Master",
        author: "Author 1",
        status: 100,
        performer: "Performer 1",
        type: "DXF",
        // resultOptions: [
        //     {
        //         materials: {
        //             tabName: "Материалы",
        //             tables: [
        //                 {
        //                     name: "Table 1",
        //                     values: [
        //                         {
        //                             id: 1,
        //                             name: "Value 1",
        //                             diameter1: 10,
        //                             diameter2: 20,
        //                             diameter3: 30,
        //                             angle: 45,
        //                             direction: "Right"
        //                         },
        //                         {
        //                             id: 2,
        //                             name: "Value 2",
        //                             diameter1: 15,
        //                             diameter2: 25,
        //                             diameter3: 35,
        //                             angle: 60,
        //                             direction: "Left"
        //                         }
        //                     ]
        //                 },
        //                 {
        //                     name: "Table 2",
        //                     values: [
        //                         {
        //                             id: 3,
        //                             name: "Value 3",
        //                             diameter1: 12,
        //                             diameter2: 22,
        //                             diameter3: 32,
        //                             angle: 50,
        //                             direction: "Right"
        //                         },
        //                         {
        //                             id: 4,
        //                             name: "Value 4",
        //                             diameter1: 17,
        //                             diameter2: 27,
        //                             diameter3: 37,
        //                             angle: 65,
        //                             direction: "Left"
        //                         }
        //                     ]
        //                 },
        //                 {
        //                     name: "Table 3",
        //                     values: [
        //                         {
        //                             id: 3,
        //                             name: "Value 3",
        //                             diameter1: 12,
        //                             diameter2: 22,
        //                             diameter3: 32,
        //                             angle: 50,
        //                             direction: "Right"
        //                         },
        //                         {
        //                             id: 4,
        //                             name: "Value 4",
        //                             diameter1: 17,
        //                             diameter2: 27,
        //                             diameter3: 37,
        //                             angle: 65,
        //                             direction: "Left"
        //                         }
        //                     ]
        //                 },
        //                 {
        //                     name: "Table 4",
        //                     values: [
        //                         {
        //                             id: 3,
        //                             name: "Value 3",
        //                             diameter1: 12,
        //                             diameter2: 22,
        //                             diameter3: 32,
        //                             angle: 50,
        //                             direction: "Right"
        //                         },
        //                         {
        //                             id: 4,
        //                             name: "Value 4",
        //                             diameter1: 17,
        //                             diameter2: 27,
        //                             diameter3: 37,
        //                             angle: 65,
        //                             direction: "Left"
        //                         }
        //                     ]
        //                 },
        //                 {
        //                     name: "Table 5",
        //                     values: [
        //                         {
        //                             id: 3,
        //                             name: "Value 3",
        //                             diameter1: 12,
        //                             diameter2: 22,
        //                             diameter3: 32,
        //                             angle: 50,
        //                             direction: "Right"
        //                         },
        //                         {
        //                             id: 4,
        //                             name: "Value 4",
        //                             diameter1: 17,
        //                             diameter2: 27,
        //                             diameter3: 37,
        //                             angle: 65,
        //                             direction: "Left"
        //                         }
        //                     ]
        //                 },
        //                 {
        //                     name: "Table 6",
        //                     values: [
        //                         {
        //                             id: 3,
        //                             name: "Value 3",
        //                             diameter1: 12,
        //                             diameter2: 22,
        //                             diameter3: 32,
        //                             angle: 50,
        //                             direction: "Right"
        //                         },
        //                         {
        //                             id: 4,
        //                             name: "Value 4",
        //                             diameter1: 17,
        //                             diameter2: 27,
        //                             diameter3: 37,
        //                             angle: 65,
        //                             direction: "Left"
        //                         }
        //                     ]
        //                 },
        //                 {
        //                     name: "Table 7",
        //                     values: [
        //                         {
        //                             id: 3,
        //                             name: "Value 3",
        //                             diameter1: 12,
        //                             diameter2: 22,
        //                             diameter3: 32,
        //                             angle: 50,
        //                             direction: "Right"
        //                         },
        //                         {
        //                             id: 4,
        //                             name: "Value 4",
        //                             diameter1: 17,
        //                             diameter2: 27,
        //                             diameter3: 37,
        //                             angle: 65,
        //                             direction: "Left"
        //                         }
        //                     ]
        //                 }
        //             ]
        //         },
        //         connectionPoints: {
        //             tabName: "Точки подключения",
        //             table: [
        //                 {
        //                     order: "Order 1",
        //                     type: "Type 1",
        //                     diameter: 10,
        //                     X: 0,
        //                     Y: 0,
        //                     Z: 0,
        //                 },
        //                 {
        //                     order: "Order 2",
        //                     type: "Type 2",
        //                     diameter: 15,
        //                     X: 1,
        //                     Y: 1,
        //                     Z: 1,
        //                 }
        //             ],
        //             image: base64
        //         },
        //         graph: {
        //             tabName: "Граф подключения фитингов",
        //             table: [
        //                 {
        //                     graph: "Graph 1",
        //                     material: "Material 1",
        //                     probability: 0.9,
        //                 },
        //                 {
        //                     graph: "Graph 2",
        //                     material: "Material 2",
        //                     probability: 0.8,
        //                 },
        //                 {
        //                     graph: "Graph 2",
        //                     material: "Material 2",
        //                     probability: 0.8,
        //                 },
        //                 {
        //                     graph: "Graph 2",
        //                     material: "Material 2",
        //                     probability: 0.8,
        //                 },
        //                 {
        //                     graph: "Graph 2",
        //                     material: "Material 2",
        //                     probability: 0.8,
        //                 },
        //                 {
        //                     graph: "Graph 2",
        //                     material: "Material 2",
        //                     probability: 0.8,
        //                 },
        //                 {
        //                     graph: "Graph 2",
        //                     material: "Material 2",
        //                     probability: 0.8,
        //                 },
        //                 {
        //                     graph: "Graph 2",
        //                     material: "Material 2",
        //                     probability: 0.8,
        //                 },
        //                 {
        //                     graph: "Graph 2",
        //                     material: "Material 2",
        //                     probability: 0.8,
        //                 },
        //                 {
        //                     graph: "Graph 2",
        //                     material: "Material 2",
        //                     probability: 0.8,
        //                 },
        //                 {
        //                     graph: "Graph 2",
        //                     material: "Material 2",
        //                     probability: 0.8,
        //                 },
        //                 {
        //                     graph: "Graph 2",
        //                     material: "Material 2",
        //                     probability: 0.8,
        //                 },
        //                 {
        //                     graph: "Graph 2",
        //                     material: "Material 2",
        //                     probability: 0.8,
        //                 }
        //             ],
        //             image: base64
        //         },
        // },
        // Another resultOptions object...
        // ]
    };

    try {
        // const {data} = yield call(Api.Projects.getProjectInfo, payload);
        yield put(Actions.Projects._getSelectedProjectSuccess(data));
    } catch (error) {
        yield put(Actions.Projects._getSelectedProjectError());
        notification({
            type: "error",
            message: "При загрузке проекта произошла ошибка"
        });
    }
};

export default function* () {
    yield takeLatest(Actions.Projects.getSelectedProject, getSelectedProject);
}
