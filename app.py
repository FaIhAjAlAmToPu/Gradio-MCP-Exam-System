import gradio as gr
from langchain_core.prompts import PromptTemplate
from langchain.chat_models import init_chat_model
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime



# Pydantic models for structured output
class Question(BaseModel):
    question_text: str
    marks: int

class Questions(BaseModel):
    questions: List[Question]

class EvaluationResult(BaseModel):
    marks_obtained: int
    feedback: str

class EvaluationResults(BaseModel):
    evaluations: List[EvaluationResult]
    deduction: int

# Initialize the model with structured output
model = init_chat_model(
    model="mistral-large-latest",
    model_provider="mistralai"
).with_structured_output(Questions)

def generate_questions(subject, topic, num_questions, marks_per_question, total_time, comment):
    # Updated LangChain prompt template for question generation
    prompt_template = PromptTemplate(
        input_variables=["subject", "topic", "num_questions", "marks_per_question", "total_time", "comment"],
        template="""
        You are an expert educational content creator tasked with generating high-quality exam questions.
        Create {num_questions} unique exam questions for the subject '{subject}' on the topic '{topic}'.
        Each question should be worth {marks_per_question} marks and designed to fit within a total exam duration of {total_time} minutes.
        Consider the following comment(if any) for context or specific instructions: '{comment}'.
        Ensure the questions are clear, concise, and appropriate for the subject and topic, with no duplicates.
        """
    )
    
    # Format the prompt with input values
    formatted_prompt = prompt_template.format(
        subject=subject,
        topic=topic,
        num_questions=num_questions,
        marks_per_question=marks_per_question,
        total_time=total_time,
        comment=comment
    )
    
    # Generate questions
    response = model.invoke(formatted_prompt)
    
    # Format all questions for display
    questions = Questions(questions=response.questions)
    display_output = f"**Generated Questions for {subject} - {topic}:**\n\n"
    for i, q in enumerate(questions.questions, start=1):
        display_output += f"Q{i}. {q.question_text} ({q.marks} marks)\n\n"
    display_output += f"**Total Time:** {total_time} minutes\n"
    
    return display_output, questions, datetime.now()

eval_model = init_chat_model(
    model="mistral-large-latest",
    model_provider="mistralai"
).with_structured_output(EvaluationResults)

def evaluate_answers(answers, questions, total_time, start_time):
    # Calculate time taken
    end_time = datetime.now()
    time_taken = end_time - start_time
    time_taken_minutes = time_taken.total_seconds() / 60
    
    # Prepare evaluation prompt with instructions for AI to calculate time deduction
    evaluation_prompt_template = PromptTemplate(
        input_variables=["questions", "answers", "total_time", "time_taken_minutes"],
        template="""
        You are an expert examiner tasked with evaluating student answers and determining a time-based deduction.
        The student has provided answers in a single text block, where each answer is prefixed with the question number (e.g., '1. [answer]', '2. [answer]').
        Match each answer to its corresponding question based on the question number.
        The questions and their maximum marks are provided below. Evaluate each answer for correctness, clarity, and completeness.
        Assign marks_obtained for each question based on its quality, without considering time.
        Separately, calculate a time-based deduction to be applied to the total marks:
        - If time taken is within or below allocated time, no deduction applies.
        - The more time taken by the student exceeds the allocated time the more marks will be deducted.
        Return the marks obtained and feedback for each question, and a single deduction value for time overrun. 
        And if any question does not have answer give 0 marks and also give hints of the solution as feedback.
        Questions:
        {questions}
        Student Answers:
        {answers}
        Allocated Time:
        {total_time} minutes
        Time Taken:
        {time_taken_minutes:.2f} minutes
        """
    )
    
    # Format questions
    questions_text = "\n".join([f"{i+1}. {q.question_text} (Marks: {q.marks})" for i, q in enumerate(questions.questions)])
    
    # Format evaluation prompt
    formatted_eval_prompt = evaluation_prompt_template.format(
        questions=questions_text,
        answers=answers,
        total_time=total_time,
        time_taken_minutes=time_taken_minutes
    )
    
    # Evaluate answers
    evaluation_response = eval_model.invoke(formatted_eval_prompt)
    
    # Calculate total marks
    total_marks_possible = sum(q.marks for q in questions.questions)
    total_marks_obtained = sum(eval.marks_obtained for eval in evaluation_response.evaluations)
    final_marks = max(0, total_marks_obtained - evaluation_response.deduction)
    
    # Format evaluation results for display
    display_output = "**Evaluation Results:**\n\n"
    for i, eval in enumerate(evaluation_response.evaluations, 1):
        display_output += f"**Question {i}:** Marks Obtained: {eval.marks_obtained}/{questions.questions[i-1].marks}, Feedback: {eval.feedback}\n\n"
    
    # Add time and marks summary
    display_output += f"**Time Summary:**\n"
    display_output += f"- Allocated Time: {total_time} minutes\n"
    display_output += f"- Time Taken: {time_taken_minutes:.2f} minutes\n"
    if time_taken_minutes > total_time:
        display_output += f"- Excess Time: {(time_taken_minutes - total_time):.2f} minutes\n"
        display_output += f"- Time Deduction: {evaluation_response.deduction} marks\n"
    else:
        display_output += "- No time deduction applied.\n"
    
    display_output += f"\n**Marks Summary:**\n"
    display_output += f"- Marks Before Deduction: {total_marks_obtained}/{total_marks_possible}\n"
    if evaluation_response.deduction > 0:
        display_output += f"- Marks After Time Deduction: {final_marks}/{total_marks_possible}\n"
    display_output += f"- **Final Score**: {final_marks}/{total_marks_possible}\n"
    
    return display_output
    

# Build the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Exam Question Generator and Answer Evaluator")
    
    with gr.Row():
        subject = gr.Textbox(label="Subject", placeholder="e.g., Mathematics")
        topic = gr.Textbox(label="Topic", placeholder="e.g., Calculus")
    
    with gr.Row():
        num_questions = gr.Number(label="Number of Questions", value=5, minimum=1, step=1)
        marks_per_question = gr.Number(label="Marks per Question", value=10, minimum=1, step=1)
    
    total_time = gr.Number(label="Total Exam Time (minutes)", value=60, minimum=1, step=1)
    comment = gr.Textbox(label="Additional Comments", placeholder="e.g., Focus on application-based questions")
    
    generate_button = gr.Button("Generate Questions")
    exam_center = gr.Markdown(label="Exam Center: Generated Questions")
    
    questions_state = gr.State()
    start_time_state = gr.State()
    
    # Generate questions and update UI
    generate_button.click(
        fn=generate_questions,
        inputs=[subject, topic, num_questions, marks_per_question, total_time, comment],
        outputs=[exam_center, questions_state, start_time_state]
    )
    
    answer_box = gr.Textbox(label="Enter Answers", lines=10, placeholder="Enter answers with question numbers, e.g., '1. [answer for question 1]\n2. [answer for question 2]'")
    submit_answers_button = gr.Button("Submit Answers for Evaluation")
    evaluation_output = gr.Markdown(label="Evaluation Results")
    
    # Evaluate answers
    submit_answers_button.click(
        fn=evaluate_answers,
        inputs=[answer_box, questions_state, total_time, start_time_state],
        outputs=evaluation_output
    )

# Launch the app
demo.launch()