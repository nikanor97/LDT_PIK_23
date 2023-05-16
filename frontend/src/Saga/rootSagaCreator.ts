import {all, spawn, call} from "redux-saga/effects";

export default function* (sagas: any[], name: string) {
    yield all(
        sagas.map((saga) => spawn(function* () {
            while (true) {
                try {
                    yield call(saga);
                    break;
                } catch (error) {
                    console.log(`SAGA ${name} ERROR`,error);
                }
            }
        }))
    );
    if (process.env.NODE_ENV === "development") {
        console.log(`SAGA ${name}: runned`);
    }
}
