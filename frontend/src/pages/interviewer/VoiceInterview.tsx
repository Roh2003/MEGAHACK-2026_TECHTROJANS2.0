import { useState, useEffect, useRef } from "react"
import Vapi from "@vapi-ai/web"
import { Question } from "@/types"

interface Props {
questions: Question[];
parsedSkills: string[]
}


const dummyQuestions:Question[]=[

]

const buildInterviewInstructions = (questions: Question[]) => {

if (!questions.length) {
return `
Conduct a job interview.
Ask questions one by one.
Wait for candidate response.
`
}

const orderedQuestions = questions
	.map((q, index) => {
		// const level = q.level ? `Level: ${q.level}. ` : ""
		// const category = q.category ? `Category: ${q.category}. ` : ""
		return `${index + 1}. ${q.question}`.trim()
	})
	.join("\n\n")

return `
Hi, you are an AI voice interviewer.

Interview rules:
1. Ask only the questions listed below.
2. Ask one question at a time in the exact order.
3. After each answer, briefly acknowledge and move to the next question.
4. Do not reveal scoring rubric or expected topics.
5. Do not add new questions unless the candidate asks to repeat a question.
6. If the candidate is silent, politely ask again once.
7. After the last question, thank the candidate and end the interview.

Question set:
${orderedQuestions}
`
}

const VoiceInterview = ({questions, parsedSkills}: Props) => {

const [vapi,setVapi] = useState<Vapi | null>(null)
const [isConnected,setIsConnected] = useState(false)
const [isSpeaking,setIsSpeaking] = useState(false)
const [time,setTime] = useState(0)
const [startError,setStartError] = useState("")
const vapiRef = useRef<Vapi | null>(null)


console.log(
    "questions", questions
)

useEffect(()=>{

let timer:NodeJS.Timeout

if(isConnected){

timer = setInterval(()=>{

setTime((prev)=>prev+1)

},1000)

}

return ()=>clearInterval(timer)

},[isConnected])

const formatTime = (seconds:number)=>{

const m = Math.floor(seconds/60)
const s = seconds % 60

return `${m}:${s < 10 ? "0"+s : s}`

}
const getVapiInstance = () => {
	if (!vapiRef.current) {
		vapiRef.current = new Vapi("724aebb7-ce38-4ed5-9d72-8791be10ae6b")
	}

	return vapiRef.current
}

const firstName="Souvik Mondal";
const jobTitle="Python Developer"


const startCall=async()=>{

if (!questions.length) {
	return
}

if (!navigator?.mediaDevices?.getUserMedia) {
	setStartError("This browser does not support microphone access required for voice interview.")
	return
}

try {
	await navigator.mediaDevices.getUserMedia({ audio: true })
} catch {
	setStartError("Microphone permission is blocked. Please allow mic access and try again.")
	return
}

setStartError("")
const vapiInstance = getVapiInstance()
setVapi(vapiInstance)

vapiInstance.removeAllListeners()
    

    const assistantOptions={
        name: "AI Recruiter",
        firstMessage: "Hi "+ firstName +", how are you ? ready for your interview on " + jobTitle,
        firstMessageMode: "assistant-speaks-first",
        transcriber:{
            provider: "deepgram",
            model: "nova-2",
            language: "en-US",
        },
        voice: {
            provider: "playht",
            voiceId: "jennifer",
        },
        model:{
            provider: "openai",
            model: "gpt-4",
            messages:[
                {
                    role: "system",
                    content: `
                    You are an AI assistant conducting interviews.

Your job is to ask candidate provided interview questions, assess their responses.

Begin the conversation with a friendly introduction, setting a relaxed yet professional tone. Example:
"Hey there! Welcome to your ${jobTitle} interview. Let’s get started with a few questions."

Ask one question at a time and wait for the candidate’s response before proceeding. Keep the questions clear and concise. Below are the questions: ${questions.map((q,index)=>`${index+1}. ${q.question}`).join("\n")}

If the candidate struggles, offer hints or rephrase the question without giving away the answer. Example:
"Need a hint? Think about how React tracks component updates!"

Provide brief, encouraging feedback after each answer. Example:
"Nice! That’s a solid answer."
"Hmm, not quite! Want to try again?"

Keep the conversation natural and engaging — use casual phrases like
"Alright, next up..." or "Let’s tackle a tricky one!"

After 5–7 questions, wrap up the interview smoothly by summarizing their performance. Example:
"That was great! You handled some tough questions well. Keep sharpening your skills!"

End on a positive note:
"Thanks for chatting! Hope to see you crushing projects soon!"

Key Guidelines:
✓ Be friendly, engaging, and witty
✓ Keep responses short and natural, like a real conversation
✓ Adapt based on the candidate’s confidence level
✓ Ensure the interview remains focused on ${parsedSkills.join(", ").trim()}
                    `
                }
            ]
        }
    }

    void vapiInstance.start(assistantOptions as any).catch((error: unknown) => {
		if (error instanceof Error) {
			setStartError(error.message)
			return
		}

		setStartError("Unable to start interview. Please try again.")
	})

	vapiInstance.on("call-start",()=>{

	setIsConnected(true)
	setStartError("")

	})

	vapiInstance.on("call-end",()=>{

	setIsConnected(false)
	setIsSpeaking(false)
	setTime(0)

	})

	vapiInstance.on("speech-start",()=>{

	setIsSpeaking(true)

	})

	vapiInstance.on("speech-end",()=>{

	setIsSpeaking(false)

	})

	vapiInstance.on("error",(error: unknown)=>{
		if (error instanceof Error) {
			setStartError(error.message)
			return
		}

		setStartError("Unable to start interview. Please verify your Vapi setup.")
	})

	vapiInstance.on("call-start-failed",(event: unknown)=>{
		if (event && typeof event === "object" && "stage" in event) {
			setStartError(`Call start failed at stage: ${String((event as { stage?: string }).stage || "unknown")}`)
			return
		}

		setStartError("Call start failed before the meeting connected.")
	})

	vapiInstance.on("message",(message: unknown)=>{
		if (!message || typeof message !== "object") {
			return
		}

		const maybeMsg = message as { type?: string; message?: string; status?: string }
		if (maybeMsg.type === "status-update" && maybeMsg.status === "ended") {
			setStartError("Meeting ended by server. Please verify model/voice settings and account limits.")
		}

		if (maybeMsg.type === "error") {
			setStartError(maybeMsg.message || "Voice call error received from Vapi.")
		}
	})
}
// const startInterview = () => {

// if (!questions.length) {
// return
// }

// setStartError("")


// setVapi(vapiInstance)

// const instructions = buildInterviewInstructions(questions)

// void vapiInstance.start({
// 	model: {
// 		provider: "google",
// 		model: "gemini-2.0-flash",
// 		messages: [
// 			{
// 				role: "system",
// 				content: instructions,
// 			},
// 		],
// 	},
// 	voice: {
// 		provider: "vapi",
// 		voiceId: "Elliot",
// 	},
// 	firstMessage: "Hi, welcome to your interview. Let us begin.",
// 	firstMessageMode: "assistant-speaks-first",
// } as any).catch((error: unknown) => {
// 	if (error instanceof Error) {
// 		setStartError(error.message)
// 		return
// 	}

// 	setStartError("Unable to start interview. Please try again.")
// })

// vapiInstance.on("call-start",()=>{

// setIsConnected(true)
// setStartError("")

// })

// vapiInstance.on("call-end",()=>{

// setIsConnected(false)
// setIsSpeaking(false)
// setTime(0)

// })

// vapiInstance.on("speech-start",()=>{

// setIsSpeaking(true)

// })

// vapiInstance.on("speech-end",()=>{

// setIsSpeaking(false)

// })

// vapiInstance.on("error",(error: unknown)=>{
// 	if (error instanceof Error) {
// 		setStartError(error.message)
// 		return
// 	}

// 	setStartError("Unable to start interview. Please verify your Vapi setup.")
// })

// }

const endInterview = ()=>{
const confirmed = confirm("Are you sure you want to end the interview?")

if (confirmed && vapi) {
	void vapi.stop()
}

}

return(

<div className="h-screen bg-gray-900 flex flex-col">

{/* Top Bar */}

<div className="flex justify-between items-center p-4 text-white">

<h1 className="text-xl font-semibold">

AI Interview Session

</h1>

<div className="bg-black px-4 py-2 rounded-lg">

⏱ {formatTime(time)}

</div>

</div>

{/* Video Panels */}

<div className="flex flex-1 gap-4 p-4">

{/* AI Recruiter */}

<div className="flex-1 bg-gray-800 rounded-xl flex flex-col items-center justify-center text-white relative">

<div className={`w-24 h-24 rounded-full bg-purple-500 flex items-center justify-center text-3xl ${isSpeaking ? "animate-pulse" : ""}`}>

🤖

</div>

<p className="mt-4 font-medium">

AI Recruiter

</p>

{isSpeaking && (

<span className="text-green-400 text-sm mt-2">

Speaking...

</span>

)}

</div>

{/* Candidate */}

<div className="flex-1 bg-gray-800 rounded-xl flex flex-col items-center justify-center text-white">

<div className="w-24 h-24 rounded-full bg-blue-500 flex items-center justify-center text-3xl">

👤

</div>

<p className="mt-4 font-medium">

Candidate

</p>

</div>

</div>

{/* Bottom Controls */}

<div className="flex justify-center items-center gap-6 pb-6">

{!isConnected ? (

<button
onClick={startCall}
disabled={!questions.length}
className="bg-green-600 hover:bg-green-700 disabled:bg-gray-500 disabled:cursor-not-allowed text-white px-8 py-3 rounded-full text-lg shadow-lg"
>

Start Interview 🎤

</button>

) : (

<>

<button
className="bg-gray-700 hover:bg-gray-600 text-white w-14 h-14 rounded-full flex items-center justify-center text-xl"
>

🎤

</button>

<button
onClick={endInterview}
className="bg-red-600 hover:bg-red-700 text-white w-16 h-16 rounded-full flex items-center justify-center text-xl shadow-lg"
>

📞

</button>

</>

)}

</div>

{!isConnected && (
<p className="pb-6 text-center text-sm text-gray-300">
{questions.length > 0
	? `Loaded ${questions.length} questions for voice interview.`
	: "Generate interview questions first to start voice interview."}
</p>
)}

{startError && (
<p className="pb-6 text-center text-sm text-red-400">
{startError}
</p>
)}

</div>

)

}

export default VoiceInterview