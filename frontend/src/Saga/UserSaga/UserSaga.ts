import rootSagaCreator from "../rootSagaCreator";
import UserInfoSaga from "./UserInfoSaga";

export default function* rootSaga() {
    yield rootSagaCreator([
        UserInfoSaga,
    ], "USER");
}
