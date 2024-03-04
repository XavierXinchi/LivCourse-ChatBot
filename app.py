import gradio as gr
from service import Service

def course_bot(message, history):
    service = Service()
    answer = service.answer(message, history)
    return answer['output']

# css = '''
# .gradio-container { max-width:850px !important; margin:20px auto !important;}
# .message { padding: 10px !important; font-size: 14px !important;}
# '''

css = """
.gradio-container { 
    max-width: 850px; 
    margin: 40px auto; 
    border: 1px solid #EAEAEA; 
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    border-radius: 10px;
    background-color: #FAFAFA; 
}

.gradio-app header {
    background-color: #5D3FD3;
    color: white;
    padding: 20px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-size: 1.5em;
    text-align: center;
}

.gradio-app header h1 {
    text-align: center;
}

.message {
    padding: 12px;
    font-size: 14px;
    border-radius: 20px;
    margin: 8px;
    border: 1px solid #ddd;
}
"""

app = gr.ChatInterface(
    css = css,
    fn = course_bot, 
    title = 'LivCourse-ChatBot',
    chatbot = gr.Chatbot(height=500, bubble_full_width=False),
    theme = gr.themes.Default(spacing_size='sm', radius_size='sm'),
    textbox=gr.Textbox(placeholder="Enter your questions here", container=False, scale=7),
    examples = ['who are you?', 'Introduce the campus gym', 'What are the academic years included in the Aerospace Engineering BEng (Hons) at the university of liverpool?', 
                'What is the code of ELECTRICAL CIRCUITS FOR ENGINEERS?', 'What is the description of the module ELECTRICAL CIRCUITS FOR ENGINEERS?', 
                'What optional modules does Computer Science BSc (Hons) with Computer Science BSc (Hons) Year2 include at the university of liverpool?', 
                'How many modules the university of liverpool offered in Computer Science BSc (Hons) with Computer Science BSc (Hons) Year3?'],
    submit_btn = gr.Button('Submit', variant='primary'),
    clear_btn = gr.Button('Clear chat history'),
    retry_btn = None,
    undo_btn = None,
)

if __name__ == '__main__':
    app.launch(share=True, debug=True)