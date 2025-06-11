## Project Title  
**Exam Question Generator and Answer Evaluator**

### Overview  
This application allows educators to:  
1. Generate custom exam questions for any subject and topic.  
2. Evaluate student answers with automated feedback and deductions for exceeding the allocated time.  

It uses the **LangChain framework**, **Gradio for the UI**, and **Pydantic models** to structure input/output for consistency and reliability.  

---

## 📽️ Demo

Check out the YouTube demo video here https://youtu.be/Lu5QsKOSMgo
<br>
> **OR** click the image below to watch the full demo on YouTube.<br>
[![Watch the demo](https://img.youtube.com/vi/Lu5QsKOSMgo/0.jpg)](https://youtu.be/Lu5QsKOSMgo)

Go to huggingface and [visit our space](https://huggingface.co/spaces/Agents-MCP-Hackathon/Your-Exam-System) to participate in an exam yourself.

### Key Features  
1. **Question Generation**:  
   - Generate clear, concise, and relevant exam questions based on the specified subject, topic, and criteria (marks, duration, etc.).  

2. **Automated Evaluation**:  
   - Analyze and grade answers while providing detailed feedback.  
   - Calculate and apply time-based deductions if the student exceeds the allocated time.  

3. **Structured Output**:  
   - Leverages **Pydantic models** for clean and maintainable code.  

4. **User Interface**:  
   - **Gradio** enables intuitive interaction with inputs for question criteria and a submission box for answers.  

---

### Technologies Used  
- **LangChain** for structured prompts and interaction with AI models.  
- **Gradio** for user-friendly frontend development.  
- **Mistral-Large-Latest** chat model for high-quality language generation and evaluation.  
- **Python 3.10+** and libraries like **Pydantic** for robust backend modeling.  

---
