import {Auth} from "@root/Api/AuthApi/types";
import {RequestShortState} from "@root/Utils/Redux/types";

export type fieldsError = {
    username?: string[],
    password?: string[],
    email?: string[],
}
export declare namespace iState {
    type Value = {
        registration: RequestShortState,
        login: RequestShortState,
    }
}
export declare namespace iActions {
    type userLogin = Auth.iLogin & {
        setFieldsErrors: (errors: Error) => any,
        redirect: () => any
    };
    type userRegistration = Auth.iRegistration & {
        setFieldsErrors: (errors: Error) => any,
        redirect: () => any
    };
}
