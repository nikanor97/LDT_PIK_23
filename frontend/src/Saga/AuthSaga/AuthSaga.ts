import rootSagaCreator from "../rootSagaCreator";
import UserLoginSaga from "./UserLoginSaga";
import UserRegistrationSaga from "./UserRegistrationSaga";

export default function* rootSaga() {
    yield rootSagaCreator([
        UserLoginSaga,
        UserRegistrationSaga,
    ], "AUTH");
}
