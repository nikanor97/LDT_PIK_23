export type jwtToken = {
    exp: number,
    jti: string,
    token_type: string,
    user_id: number,
}
export const decode = (jwt: string) => {
    const token_parts = jwt.split(/\./);
    return JSON.parse(window.atob(token_parts[1]));
};
