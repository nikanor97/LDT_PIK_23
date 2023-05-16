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
        email: string,
        password: string,
    }
    type oLogin = {
        access_token: string,
        refresh_token: string,
        access_expires_at: number,
        refresh_expires_at: number
    }
    type iRefresh = {
        refresh: string
    }
    type oRefresh = {
        access_token: string,
        refresh_token: string,
        access_expires_at: number,
        refresh_expires_at: number
    }
}
