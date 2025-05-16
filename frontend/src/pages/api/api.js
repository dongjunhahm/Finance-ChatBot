import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export async function askQuestion(question) {
  try {
    const res = await axios.post(
      `${BASE_URL}/ask`,
      { question },
      {
        headers: { "Content-Type": "application/json" },
      }
    );
    return res.data; // { answer: "..." }
  } catch (err) {
    return Promise.reject({
      status: err.response?.status,
      data: err.response?.data,
    });
  }
}
