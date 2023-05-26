import {combineReducers} from "redux";
import User from "./User/UserRedux";
import Auth from "./Auth/AuthRedux";
import Projects from "./Projects/ProjectsRedux";

export default combineReducers({
    User,
    Auth,
    Projects
});
