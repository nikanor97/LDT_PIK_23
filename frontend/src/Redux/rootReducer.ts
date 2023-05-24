import {combineReducers} from "redux";
import User from "./User/UserRedux";
import Auth from "./Auth/AuthRedux";

export default combineReducers({
    User,
    Auth,
});
