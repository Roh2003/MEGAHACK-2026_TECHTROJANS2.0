import { useState } from "react"
import InterviewForm from "./InterviewForm"
import QuestionsList from "./QuestionsList"
import ScheduleInterview from "./ScheduleInterview"
import VoiceInterview from "./VoiceInterview"
import { Question } from "@/types"
// import InterviewForm from "../components/InterviewForm"
// import QuestionsList from "../components/QuestionsList"
// import ScheduleInterview from "../components/ScheduleInterview"
// import VoiceInterview from "../components/VoiceInterview"
// import { Question } from "../types/types"

const InterviewerDashboard = () => {

const [questions,setQuestions]=useState<Question[]>([])
const [skills,setSkills]=useState("")
const parsedSkills = skills
	.split(",")
	.map((skill) => skill.trim())
	.filter(Boolean)

return(

<div className="min-h-screen p-10">

<div className="max-w-5xl mx-auto space-y-10">

<h1 className="text-4xl font-bold text-center">
AI Interviewer
</h1>

<InterviewForm skills={skills} setSkills={setSkills} setQuestions={setQuestions}/>

{questions.length>0 && (

<>
<QuestionsList questions={questions}/>
<ScheduleInterview questions={questions}/>
</>

)}

<VoiceInterview parsedSkills={parsedSkills} questions={questions}/>


</div>

</div>

)

}

export default InterviewerDashboard
