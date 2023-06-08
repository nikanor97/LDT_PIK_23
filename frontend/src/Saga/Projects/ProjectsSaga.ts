import rootSagaCreator from "../rootSagaCreator";
import GetProjectsSaga from "./ProjectsGetSaga";
import CreateProjectSaga from "./ProjectCreateSaga";
import GetFittingsGroupSaga from "./GetFittingsGroupSaga";
import GetSelectedProject from "./GetSelectedProject";
import ParseDXF from "./ParseDXF";
import StartCalcSaga from "./StartCalcSaga";
import DownloadResultSaga from "./DownloadResultSaga";
import DownloadFileSaga from "./DownloadFileSaga";
import DeleteProjectsSaga from "./DeleteProjectsSaga";

export default function* rootSaga() {
    yield rootSagaCreator([
        GetProjectsSaga,
        CreateProjectSaga,
        GetFittingsGroupSaga,
        GetSelectedProject,
        ParseDXF,
        StartCalcSaga,
        DownloadResultSaga,
        DownloadFileSaga,
        DeleteProjectsSaga
    ], "PROJECTS");
}
