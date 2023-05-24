import AuthSaga from "./AuthSaga/AuthSaga";
import UserSaga from "./UserSaga/UserSaga";
import ProjectSaga from "./Projects/ProjectsSaga"
import rootSagaCreator from "./rootSagaCreator";

export default function* rootSaga() {
    const sagas = [
        AuthSaga,
        UserSaga,
        ProjectSaga
    ];
    yield rootSagaCreator(sagas, "ROOT");
}
