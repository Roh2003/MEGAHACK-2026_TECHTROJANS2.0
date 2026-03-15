import { apiClient } from "@/lib/axios"
import { Question } from "@/types"
import { useState } from "react"
// import API from "../api/api"
// import { Question } from "../types/types"

interface Props{
questions: Question[]
}

const ScheduleInterview = ({questions}:Props) => {

const [email,setEmail]=useState("")
const [candidateId,setCandidateId]=useState("")
const [interviewId,setInterviewId]=useState("")

const createInterview = async () => {

const res = await apiClient.post("/create-interview",{

jobposition:"React Developer",
description:"Frontend role",
duration:30,
type:"technical",
question_list:questions,
useremail:email,
candidate_id:candidateId

})

setInterviewId(res.data.interview_id)

}

return(

<div className="bg-white p-8 rounded-xl shadow-lg">

<h2 className="text-xl font-semibold mb-6">
Schedule Interview
</h2>

<div className="grid gap-4">

<input
className="border p-3 rounded-lg"
placeholder="Recruiter Email"
onChange={(e)=>setEmail(e.target.value)}
/>

<input
className="border p-3 rounded-lg"
placeholder="Candidate ObjectId"
onChange={(e)=>setCandidateId(e.target.value)}
/>

<button
onClick={createInterview}
className="bg-green-600 text-white py-3 rounded-lg"
>

Create Interview

</button>

</div>

{interviewId && (

<div className="mt-6 bg-green-100 p-4 rounded">

Interview Created: {interviewId}

</div>

)}

</div>

)

}

export default ScheduleInterview