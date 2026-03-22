import "next-auth";

declare module "next-auth" {
    interface Session {
        accessToken: string;
        error?: string | undefined        
    }

    interface User {
        accessToken : string;
        refreshToken: string;
        accessTokenExpiry: number;
    }
}

declare module "next-auth/jwt" {
    interface JWT {
        accessToken: string;
        refreshToken: string;
        accessTokenExpiry: number;
        error ?: string
    }
}