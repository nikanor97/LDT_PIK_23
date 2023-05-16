import AuthSaga from "./AuthSaga/AuthSaga";
import UserSaga from "./UserSaga/UserSaga";
import rootSagaCreator from "./rootSagaCreator";

export default function* rootSaga() {
    const sagas = [
        AuthSaga,
        UserSaga,
    ];
    yield rootSagaCreator(sagas, "ROOT");
}
