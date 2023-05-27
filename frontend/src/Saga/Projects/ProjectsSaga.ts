import rootSagaCreator from "../rootSagaCreator";
import GetProjectsSaga from "./ProjectsGetSaga";
import CreateProjectSaga from "./ProjectCreateSaga";
import GetFittingsGroupSaga from "./GetFittingsGroupSaga";
import GetSelectedProject from "./GetSelectedProject";
import ParseDXF from "./ParseDXF";
import StartCalcSaga from "./StartCalcSaga";

export default function* rootSaga() {
    yield rootSagaCreator([
        GetProjectsSaga,
        CreateProjectSaga,
        GetFittingsGroupSaga,
        GetSelectedProject,
        ParseDXF,
        StartCalcSaga
    ], "PROJECTS");
}
