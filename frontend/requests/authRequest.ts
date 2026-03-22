import { signUpSchema } from "@/types/authSchema";
import axios from "axios";
import {z} from "zod";  

type SignUpSchema = z.infer<typeof signUpSchema>;

export const signUpRequest = async (
    user: SignUpSchema
) => {
    try {
        const result = await axios.post(`${process.env.BACKEND_URL}/api/v1/auth/signup`, user);
        return result.data;
    } catch (error) {
        console.log("Signup error: ", error);
        return error;
    }
}