// import { Question } from "../types/types"

import { Question } from "@/types"

interface Props{
questions: Question[]
}

const QuestionsList = ({questions}:Props) => {

const levelOrder: Array<"easy" | "medium" | "hard"> = ["easy", "medium", "hard"]

const groupedQuestions = levelOrder.map((level) => ({
	level,
	items: questions.filter((q) => (q.level || "").toLowerCase() === level),
}))

const fallbackQuestions = questions.filter(
	(q) => !levelOrder.includes(((q.level || "").toLowerCase() as "easy" | "medium" | "hard")),
)

return(

<div className="bg-white p-8 rounded-xl shadow-lg">

<h2 className="text-xl font-semibold mb-6">
Generated Questions
</h2>

<div className="space-y-4">

{groupedQuestions.map((group) => (
group.items.length > 0 ? (
<div key={group.level} className="space-y-4">
<h3 className="text-sm font-semibold uppercase tracking-wide text-gray-600">
{group.level} ({group.items.length})
</h3>

{group.items.map((q,index)=>(
<div
key={`${group.level}-${index}`}
className="border p-4 rounded-lg hover:bg-gray-50"
>

<p className="font-medium">
{index+1}. {q.question}
</p>

<div className="mt-2 flex flex-wrap gap-2 text-xs">
{q.level && (
<span className="rounded-full bg-purple-100 px-2 py-1 text-purple-700">
{q.level}
</span>
)}

{q.category && (
<span className="rounded-full bg-blue-100 px-2 py-1 text-blue-700">
{q.category}
</span>
)}

<span className="rounded-full bg-gray-100 px-2 py-1 text-gray-700">
{q.type}
</span>
</div>

{q.purpose && (
<p className="mt-3 text-sm text-gray-700">
Purpose: {q.purpose}
</p>
)}

{q.expected_topics && q.expected_topics.length > 0 && (
<p className="mt-2 text-sm text-gray-700">
Expected topics: {q.expected_topics.join(", ")}
</p>
)}

{q.difficulty_reason && (
<p className="mt-2 text-sm text-gray-600">
Why this level: {q.difficulty_reason}
</p>
)}

</div>
))}
</div>
) : null
))}

{fallbackQuestions.length > 0 && (
<div className="space-y-4">
<h3 className="text-sm font-semibold uppercase tracking-wide text-gray-600">
other ({fallbackQuestions.length})
</h3>

{fallbackQuestions.map((q,index)=>(
<div
key={`other-${index}`}
className="border p-4 rounded-lg hover:bg-gray-50"
>

<p className="font-medium">
{index+1}. {q.question}
</p>

<div className="mt-2 flex flex-wrap gap-2 text-xs">
{q.level && (
<span className="rounded-full bg-purple-100 px-2 py-1 text-purple-700">
{q.level}
</span>
)}

{q.category && (
<span className="rounded-full bg-blue-100 px-2 py-1 text-blue-700">
{q.category}
</span>
)}

<span className="rounded-full bg-gray-100 px-2 py-1 text-gray-700">
{q.type}
</span>
</div>

{q.purpose && (
<p className="mt-3 text-sm text-gray-700">
Purpose: {q.purpose}
</p>
)}

{q.expected_topics && q.expected_topics.length > 0 && (
<p className="mt-2 text-sm text-gray-700">
Expected topics: {q.expected_topics.join(", ")}
</p>
)}

{q.difficulty_reason && (
<p className="mt-2 text-sm text-gray-600">
Why this level: {q.difficulty_reason}
</p>
)}

</div>
))}
</div>
)}

</div>

</div>

)

}

export default QuestionsList