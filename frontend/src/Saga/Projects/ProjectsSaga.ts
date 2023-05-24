import rootSagaCreator from "../rootSagaCreator";
import GetProjectsSaga from "./ProjectsGetSaga";
import CreateProjectSaga from "./ProjectCreateSaga";

export default function* rootSaga() {
    yield rootSagaCreator([
        GetProjectsSaga,
        CreateProjectSaga,
    ], "PROJECTS");
}
