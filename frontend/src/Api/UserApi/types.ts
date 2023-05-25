import {iApi} from "@root/types";

export declare namespace User {
    type oGetUserInfo = {
        username: string,
        email: string,
    }
    type oGetUsersAll = iApi.Users.Item[];
}
