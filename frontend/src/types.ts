export interface Question {
  question: string
  type: string
  level?: string
  category?: string
  purpose?: string
  expected_topics?: string[]
  difficulty_reason?: string
}

export interface GenerateQuestionsRequest {
  job_description: {
    job_name: string
    skills: string[]
    experience: string
    location: string
    responsibilities: string[]
  }
}

export interface InterviewCreateRequest {
  jobposition: string
  description: string
  duration: number
  type: string
  question_list: Question[]
  useremail: string
  candidate_id: string
}