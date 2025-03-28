import os
import streamlit as st
from groq import Groq
from streamlit_tags import st_tags

# Configuration
PRIMARY_MODEL = "qwen-2.5-coder-32b"
BACKUP_MODEL = "llama3-70b-8192"
LANGUAGES = ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript", "Swift"]
THEMES = ["Neon", "Cyberpunk", "Solarized", "Dracula", "Monokai"]

# Streamlit UI Config 
st.set_page_config(
    page_title="AstraCode",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Theme
def inject_custom_css(theme="Neon"):
    theme_colors = {
        "Neon": {"primary": "#4fffb0", "secondary": "#ff4fd8", "bg": "#1a1a2e"},
        "Cyberpunk": {"primary": "#ff2a6d", "secondary": "#05d9e8", "bg": "#1a1a2e"},
        "Solarized": {"primary": "#268bd2", "secondary": "#d33682", "bg": "#fdf6e3"},
        "Dracula": {"primary": "#bd93f9", "secondary": "#ff79c6", "bg": "#282a36"},
        "Monokai": {"primary": "#a6e22e", "secondary": "#fd971f", "bg": "#272822"}
    }
    colors = theme_colors.get(theme, theme_colors["Neon"])
    
    st.markdown(f"""
    <style>
        .main {{
            background: linear-gradient(135deg, {colors['bg']} 0%, #16213e 100%) !important;
            color: white !important;
        }}
        .stTextInput input, .stSelectbox select, .stTextArea textarea {{
            color: {colors['primary']} !important;
            background: rgba(0,0,0,0.3) !important;
            border-radius: 10px !important;
        }}
        .stButton>button {{
            background: rgba(79,255,176,0.2) !important;
            border: 2px solid {colors['primary']} !important;
            color: {colors['primary']} !important;
            border-radius: 10px !important;
            transition: all 0.3s !important;
        }}
        .stButton>button:hover {{
            background: rgba(79,255,176,0.4) !important;
            transform: scale(1.05);
        }}
        .code-block {{
            border: 2px solid {colors['secondary']};
            border-radius: 15px;
            padding: 1rem;
            background: rgba(0,0,0,0.5);
            margin-bottom: 1rem;
        }}
        .sidebar .sidebar-content {{
            background: rgba(0,0,0,0.3) !important;
        }}
        h1, h2, h3 {{
            color: {colors['primary']} !important;
        }}
        .st-expander {{
            background: rgba(0,0,0,0.3) !important;
            border: 1px solid {colors['secondary']} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# Initialize Groq Client
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found! Please set it in environment variables or secrets.")
        return None
    return Groq(api_key=api_key)

# Code Generation Functions
def generate_code(query, language, model, client, complexity="Medium"):
    complexity_levels = {
        "Basic": "Generate simple code for",
        "Medium": "Generate well-structured code with comments for",
        "Advanced": "Generate production-ready code with error handling, tests, and documentation for"
    }
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": f"""
                {complexity_levels[complexity]} {query} in {language}. 
                Include comments in the code itself.
                IMPORTANT: Return ONLY the raw executable code with comments, 
                without any additional explanation before or after the code block.
                """
            }],
            temperature=0.7 if complexity == "Advanced" else 0.5,
            max_tokens=4096,
            top_p=0.95
        )
        # Extract just the code block if it's wrapped in markdown
        raw_content = completion.choices[0].message.content
        if '```' in raw_content:
            # Extract content between the first ``` and last ```
            code = raw_content.split('```')[1]
            if code.startswith(language.lower()):
                code = code[len(language.lower()):]
            return code.strip()
        return raw_content.strip()
    except Exception as e:
        st.error(f"Error generating code: {str(e)}")
        return None

# Main App Interface
def main():
    client = get_groq_client()
    if not client:
        return

    # Sidebar for settings
    with st.sidebar:
        st.title("⚙️ Settings")
        selected_theme = st.selectbox("Theme", THEMES, index=0)
        selected_language = st.selectbox("Programming Language", LANGUAGES, index=0)
        complexity = st.select_slider("Code Complexity", ["Basic", "Medium", "Advanced"], value="Medium")
        tags = st_tags(label="Add Keywords:", text="Press enter to add more", value=[], key="tags")
        
    inject_custom_css(selected_theme)

    # Main content
    st.title("AstraCode")
    st.caption("Generate production-ready code in multiple languages with a single click")

    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_area("Describe your coding requirement:", height=100, 
                            placeholder="e.g., A function to calculate Fibonacci sequence")
    
    if 'generated_code' not in st.session_state:
        st.session_state.generated_code = None
    if 'alternative_code' not in st.session_state:
        st.session_state.alternative_code = None

    action_cols = st.columns([1, 1, 1, 1, 2])
    with action_cols[0]:
        if st.button("🚀 Generate Code", use_container_width=True):
            with st.spinner(f"Generating {selected_language} code..."):
                code = generate_code(query, selected_language, PRIMARY_MODEL, client, complexity)
                if not code:
                    st.warning("Trying backup model...")
                    code = generate_code(query, selected_language, BACKUP_MODEL, client, complexity)
                
                if code:
                    st.session_state.generated_code = code
                    st.session_state.alternative_code = None
                else:
                    st.error("Failed to generate code. Please try again.")

    with action_cols[1]:
        if st.button("🔄 Alternative", use_container_width=True, disabled=not st.session_state.generated_code):
            with st.spinner(f"Generating alternative {selected_language} solution..."):
                alt_code = generate_code(f"Alternative approach for: {query}", selected_language, PRIMARY_MODEL, client, complexity)
                if alt_code:
                    st.session_state.alternative_code = alt_code

    with action_cols[2]:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state.generated_code = None
            st.session_state.alternative_code = None

    # Display results
    if st.session_state.generated_code:
        with st.container():
            st.subheader(f"Generated {selected_language} Code")
            st.code(st.session_state.generated_code, language=selected_language.lower())
            
            # Explanation section
            with st.expander("📝 Code Explanation", expanded=True):
                if client:
                    try:
                        explanation = client.chat.completions.create(
                            model=PRIMARY_MODEL,
                            messages=[{
                                "role": "user",
                                "content": f"Explain this {selected_language} code in simple terms:\n\n{st.session_state.generated_code}"
                            }],
                            temperature=0.3,
                            max_tokens=1024
                        )
                        st.write(explanation.choices[0].message.content)
                    except Exception as e:
                        st.error(f"Error generating explanation: {str(e)}")

        if st.session_state.alternative_code:
            with st.container():
                st.subheader(f"Alternative {selected_language} Solution")
                st.code(st.session_state.alternative_code, language=selected_language.lower())

if __name__ == "__main__":
    main()