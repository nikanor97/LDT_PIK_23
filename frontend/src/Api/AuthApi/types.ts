export declare namespace Auth {
    type iRegistration = {
        username: string,
        password: string,
        email: string,
    }
    type oRegistration = {
        username: string,
        email: string
    }
    type iLogin = {
        username: string,
        password: string,
    }
    type oLogin = {
        access: string,
        refresh: string
    }
    type iRefresh = {
        refresh: string
    }
    type oRefresh = {
        access: string,
        refresh: string
    }
}
