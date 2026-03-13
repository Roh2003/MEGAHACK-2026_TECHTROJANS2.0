import { useState } from "react"
// import API from "../api/api"
// import { Question } from "../types/types"
import { apiClient } from "@/lib/axios"
import { Question } from "@/types"

interface Props{
setQuestions: (questions: Question[]) => void
}

interface ApiQuestion {
	level?: string
	category?: string
	question?: string
	purpose?: string
	expected_topics?: string[]
	difficulty_reason?: string
}

interface GenerateQuestionsApiResponse {
	success?: boolean
	questions_per_level?: number
	data?: {
		response?: {
			questions?: ApiQuestion[]
		}
	}
	response?: {
		questions?: ApiQuestion[]
	}
	questions?: ApiQuestion[]
}

const InterviewForm = ({setQuestions}:Props) => {

const [jobposition,setJobPosition]=useState("")
const [skills,setSkills]=useState("")
const [experience,setExperience]=useState("3+ years")
const [location,setLocation]=useState("Remote")
const [responsibilities,setResponsibilities]=useState("")
const [loading,setLoading]=useState(false)
const [error,setError]=useState("")

const generateQuestions = async () => {

setLoading(true)
setError("")

try {

const parsedSkills = skills
	.split(",")
	.map((skill) => skill.trim())
	.filter(Boolean)

const parsedResponsibilities = responsibilities
	.split(",")
	.map((item) => item.trim())
	.filter(Boolean)

	const res = await apiClient.post<GenerateQuestionsApiResponse>("/ai-interview/questions",{
	job_description: {
		job_name: jobposition,
		skills: parsedSkills,
		experience,
		location,
		responsibilities: parsedResponsibilities,
	},
	questions_per_level: 5,
	model: "gemini-1.5-flash"

})

	const rawQuestions: ApiQuestion[] =
		res.data?.data?.response?.questions ??
		res.data?.response?.questions ??
		res.data?.questions ??
		[]

const formattedQuestions: Question[] = rawQuestions
	.filter((item) => Boolean(item?.question))
	.map((item) => ({
		question: item.question || "",
		type: `${item.category || "technical"}-${item.level || "easy"}`,
		level: item.level,
		category: item.category,
		purpose: item.purpose,
		expected_topics: item.expected_topics || [],
		difficulty_reason: item.difficulty_reason,
	}))

setQuestions(formattedQuestions)

if (!formattedQuestions.length) {
	setError("No questions were returned by the API.")
}

} catch {
	setQuestions([])
	setError("Failed to generate questions. Please check API connection and try again.")
} finally {
	setLoading(false)
}

}

return(

<div className="bg-white p-8 rounded-xl shadow-lg">

<h2 className="text-2xl font-bold mb-6">
Create Interview
</h2>

<div className="grid gap-4">

<input
className="border p-3 rounded-lg"
placeholder="Job Position"
value={jobposition}
onChange={(e)=>setJobPosition(e.target.value)}
/>

<input
className="border p-3 rounded-lg"
placeholder="Experience (e.g. 3+ years)"
value={experience}
onChange={(e)=>setExperience(e.target.value)}
/>

<input
className="border p-3 rounded-lg"
placeholder="Location (e.g. Remote)"
value={location}
onChange={(e)=>setLocation(e.target.value)}
/>

<input
className="border p-3 rounded-lg"
placeholder="Skills (Python, FastAPI, MongoDB)"
value={skills}
onChange={(e)=>setSkills(e.target.value)}
/>

<textarea
className="border p-3 rounded-lg"
placeholder="Responsibilities (Build REST APIs, Design scalable backend services)"
value={responsibilities}
onChange={(e)=>setResponsibilities(e.target.value)}
/>

<button
onClick={generateQuestions}
disabled={loading}
className="bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700"
>

{loading ? "Generating..." : "Generate Questions"}

</button>

{error && (
<p className="text-sm text-red-600">
{error}
</p>
)}

</div>

</div>

)

}

export default InterviewForm