import rootSagaCreator from "../rootSagaCreator";
import UserInfoSaga from "./UserInfoSaga";
import GetUsersAllSaga from "./GetUsersAllSaga";

export default function* rootSaga() {
    yield rootSagaCreator([
        UserInfoSaga,
        GetUsersAllSaga
    ], "USER");
}
