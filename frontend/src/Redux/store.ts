import {configureStore, getDefaultMiddleware} from "@reduxjs/toolkit";
import rootReducer from "./rootReducer";
import createSagas from "redux-saga";
import rootSaga from "../Saga/rootSaga";

const sagaMiddleware = createSagas();
const middleware = [
    ...getDefaultMiddleware({
        thunk: false,
        serializableCheck: false,
        immutableCheck: true
    }),
    sagaMiddleware
];

const store = configureStore({
    reducer: rootReducer,
    middleware
});

sagaMiddleware.run(rootSaga);

export type AppState = ReturnType<typeof rootReducer>;
export type AppDispatch = typeof store.dispatch
export default store;
