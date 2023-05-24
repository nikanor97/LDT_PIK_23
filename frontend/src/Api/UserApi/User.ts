import Request from "../Request";
import {User} from "./types";
import Endpoints from "./endpoints";

export default {
    getUserInfo: () => {
        return Request.get<User.oGetUserInfo>(`${Endpoints.user.base}`);
    },
};
