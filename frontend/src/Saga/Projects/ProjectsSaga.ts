import rootSagaCreator from "../rootSagaCreator";
import GetProjectsSaga from "./ProjectsGetSaga";
import CreateProjectSaga from "./ProjectCreateSaga";
import GetFittingsGroupSaga from "./GetFittingsGroupSaga";
import GetSelectedProject from "./GetSelectedProject";

export default function* rootSaga() {
    yield rootSagaCreator([
        GetProjectsSaga,
        CreateProjectSaga,
        GetFittingsGroupSaga,
        GetSelectedProject
    ], "PROJECTS");
}
