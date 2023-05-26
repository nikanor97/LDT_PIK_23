import rootSagaCreator from "../rootSagaCreator";
import GetProjectsSaga from "./ProjectsGetSaga";
import CreateProjectSaga from "./ProjectCreateSaga";
import GetFittingsGroupSaga from "./GetFittingsGroupSaga";

export default function* rootSaga() {
    yield rootSagaCreator([
        GetProjectsSaga,
        CreateProjectSaga,
        GetFittingsGroupSaga
    ], "PROJECTS");
}
