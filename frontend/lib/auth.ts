import NextAuth, {NextAuthOptions} from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

export const authOptions: NextAuthOptions = {
    providers: [
        CredentialsProvider({
            name: "Credentials",
            credentials: {
                email: {
                    label: "Email",
                    placeholder: "Enter your email",
                    type: "email"
                },
                password: {
                    label: "Password",
                    placeholder: "Enter your password",
                    type: "password"
                }
            },
            async authorize(credentials) {
                const res = await fetch(`${process.env.BACKEND_URL}/api/v1/auth/signin`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        email: credentials?.email,
                        password: credentials?.password,
                    }),
                })

                if (!res.ok) {
                    return null;
                }

                const tokens = await res.json();
                const accessToken = tokens.access_token as string;
                const tokenPayload = accessToken?.split(".")[1];
                const decodedPayload = tokenPayload
                    ? JSON.parse(Buffer.from(tokenPayload, "base64url").toString("utf8"))
                    : null;

                return {
                    id: decodedPayload?.sub ?? credentials?.email ?? "auth-user",
                    accessToken,
                    refreshToken: tokens.refresh_token,
                    accessTokenExpiry: Date.now() + 14 * 60 * 1000,
                }
            }
        })
    ],

    callbacks: {
        async jwt({token, user}) {
            if(user) {
                token.accessToken = user.accessToken
                token.refreshToken = user.refreshToken
                token.accessTokenExpiry = Date.now() + 14 * 60 * 1000
            }

            if (Date.now() < (token.accessTokenExpiry as number)) return token;

            const res = await fetch(`${process.env.BACKEND_URL}/api/v1/auth/refresh`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ refresh_token: token.refreshToken }),
            })

            if (!res.ok) {
                return { ...token, error: "RefreshFailed" }
            }

            const newTokens = await res.json();
            return  {
                ...token,
                accessToken: newTokens.access_token,
                refreshToken: newTokens.refresh_token,
                accessTokenExpiry: Date.now() + 14 * 60 * 1000,
            }
        },

        async session({
            session, token
        }) {
            session.accessToken = token.accessToken as string;
            session.error = token.error as string | undefined
            return session
        }
    },
    pages: {
        signIn: "/signin"
    }
}

export default NextAuth(authOptions);