import re
import io
import tempfile
import PyPDF2
import ast
from concurrent.futures import ThreadPoolExecutor

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA


class ResumeAnalysisAgent:

    def __init__(self, api_key: str, cutoff_score: int = 75):

        self.api_key = api_key
        self.cutoff_score = cutoff_score

        self.resume_text = None
        self.jd_text = None

        self.extracted_skills = []
        self.analysis_result = None

        self.rag_vectorstore = None

        self.resume_strengths = []
        self.resume_weaknesses = []

        self.improved_resume_path = None

        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=self.api_key
        )

    # ---------------------------------------------------
    # TEXT EXTRACTION
    # ---------------------------------------------------

    def extract_text_from_pdf(self, pdf_file):

        text = ""

        if hasattr(pdf_file, "getvalue"):
            pdf_bytes = io.BytesIO(pdf_file.getvalue())
            reader = PyPDF2.PdfReader(pdf_bytes)
        else:
            reader = PyPDF2.PdfReader(pdf_file)

        for page in reader.pages:
            text += page.extract_text() or ""

        return text

    def extract_text_from_txt(self, txt_file):

        if hasattr(txt_file, "getvalue"):
            return txt_file.getvalue().decode("utf-8")

        with open(txt_file, "r", encoding="utf-8") as f:
            return f.read()

    def extract_text_from_file(self, file):

        ext = file.name.split(".")[-1].lower()

        if ext == "pdf":
            return self.extract_text_from_pdf(file)

        if ext == "txt":
            return self.extract_text_from_txt(file)

        return ""

    # ---------------------------------------------------
    # VECTOR STORE
    # ---------------------------------------------------

    def create_vector_store(self, texts):

        embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)

        return FAISS.from_texts(texts, embeddings)

    # ---------------------------------------------------
    # SKILL ANALYSIS
    # ---------------------------------------------------

    def analyze_skill(self, qa_chain, skill):

        query = f"""
Analyze the resume and rate the candidate proficiency in {skill}.

Return format:
Score: number between 0-10
Reason: short explanation
"""

        response = qa_chain.run(query)

        match = re.search(r"\b(10|[0-9])\b", response)
        score = int(match.group(1)) if match else 0

        return {
            "skill": skill,
            "score": score,
            "reason": response
        }

    # ---------------------------------------------------
    # SEMANTIC SKILL ANALYSIS
    # ---------------------------------------------------

    def semantic_skill_analysis(self, resume_text, skills):

        vectorstore = self.create_vector_store([resume_text])

        retriever = vectorstore.as_retriever()

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=retriever,
            return_source_documents=False
        )

        skill_scores = {}
        missing_skills = []
        strengths = []

        total_score = 0

        with ThreadPoolExecutor(max_workers=5) as executor:

            results = list(
                executor.map(lambda s: self.analyze_skill(qa_chain, s), skills)
            )

        for res in results:

            skill = res["skill"]
            score = res["score"]

            skill_scores[skill] = score

            total_score += score

            if score <= 5:
                missing_skills.append(skill)

            if score >= 7:
                strengths.append(skill)

        overall_score = int((total_score / (10 * len(skills))) * 100) if skills else 0

        self.resume_strengths = strengths
        self.resume_weaknesses = missing_skills

        return {
            "overall_score": overall_score,
            "skill_scores": skill_scores,
            "strengths": strengths,
            "missing_skills": missing_skills
        }

    # ---------------------------------------------------
    # SKILL EXTRACTION FROM JD
    # ---------------------------------------------------

    def extract_skills_from_jd(self, jd_text):

        prompt = f"""
Extract the main technical skills from this job description.

Return ONLY a Python list of skills.

Job description:
{jd_text}
"""

        response = self.llm.invoke(prompt)

        text = response.content.strip()

        try:
            skills = ast.literal_eval(text)

            if isinstance(skills, list):
                return skills

        except:
            pass

        return [s.strip() for s in text.split(",") if s.strip()]

    # ---------------------------------------------------
    # RESUME ANALYSIS
    # ---------------------------------------------------

    def analyze_resume(self, resume_file, role_requirements=None, custom_jd=None):

        self.resume_text = self.extract_text_from_file(resume_file)

        if not self.resume_text:
            return {"error": "Could not extract resume text."}

        if custom_jd:

            self.jd_text = self.extract_text_from_file(custom_jd)

            self.extracted_skills = self.extract_skills_from_jd(self.jd_text)

        elif role_requirements:

            self.extracted_skills = role_requirements

        else:
            self.extracted_skills = []

        self.analysis_result = self.semantic_skill_analysis(
            self.resume_text,
            self.extracted_skills
        )

        return self.analysis_result

    # ---------------------------------------------------
    # CHAT WITH RESUME
    # ---------------------------------------------------

    def ask_question(self, question):

        if not self.resume_text:
            return "Please analyze a resume first."

        if not self.rag_vectorstore:

            self.rag_vectorstore = self.create_vector_store([self.resume_text])

        retriever = self.rag_vectorstore.as_retriever(search_kwargs={"k": 3})

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=retriever,
            return_source_documents=False
        )

        return qa_chain.run(question)

    # ---------------------------------------------------
    # RESUME IMPROVEMENT
    # ---------------------------------------------------

    def get_improved_resume(self, highlight_skills=""):

        if not self.resume_text:
            return "Analyze resume first."

        prompt = f"""
Improve the following resume.

Highlight these skills: {highlight_skills}

Resume:
{self.resume_text}

Return the improved resume text.
"""

        response = self.llm.invoke(prompt)

        improved_resume = response.content

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".txt",
            mode="w",
            encoding="utf-8"
        ) as f:

            f.write(improved_resume)

            self.improved_resume_path = f.name

        return improved_resume