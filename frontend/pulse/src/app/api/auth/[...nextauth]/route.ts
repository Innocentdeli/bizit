import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text", placeholder: "jsmith" },
        password: { label: "Password", type: "password" },
        role: { label: "Role", type: "text" }
      },
      async authorize(credentials, req) {
        // Mock User Database Logic
        // In production, this would verify instructions against the real database

        // Mock Business User
        if (credentials?.username === "business" || credentials?.role === "BUSINESS") {
          return {
            id: "u-biz-101",
            name: "Lagos Tech Hub",
            email: "owner@lagostechhub.com",
            image: "B",
            role: "BUSINESS"
          };
        }

        // Mock Consumer User
        if (credentials?.username === "consumer" || credentials?.role === "USER") {
          return {
            id: "u-cons-001",
            name: "Chinedu O.",
            email: "chinedu@example.com",
            image: "C",
            role: "USER"
          };
        }

        return null; // Login failed
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }: any) {
      if (user) {
        token.role = user.role;
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }: any) {
      if (session?.user) {
        session.user.role = token.role;
        session.user.id = token.id;
      }
      return session;
    }
  },
  pages: {
    signIn: '/login', // Point to our custom login page
  }
});

export { handler as GET, handler as POST };
