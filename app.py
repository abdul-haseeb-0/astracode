import os
import streamlit as st
from groq import Groq
from streamlit_tags import st_tags
import time
from typing import Optional

# Configuration
PRIMARY_MODEL = "qwen-2.5-coder-32b"
BACKUP_MODEL = "llama3-70b-8192"
LANGUAGES = ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript", "Swift", "Kotlin", "C#"]
THEMES = ["Neon", "Cyberpunk", "Solarized", "Dracula", "Monokai", "Nord", "Ocean", "Matrix"]
COMPLEXITY_LEVELS = {
    "Basic": {
        "description": "Simple implementation with minimal features",
        "icon": "🌱",
        "temperature": 0.3
    },
    "Medium": {
        "description": "Well-structured code with comments and basic error handling",
        "icon": "🚀",
        "temperature": 0.5
    },
    "Advanced": {
        "description": "Production-ready with tests, documentation, and robust error handling",
        "icon": "💎",
        "temperature": 0.7
    },
    "Expert": {
        "description": "Optimized solution with advanced patterns, benchmarks, and scalability",
        "icon": "🧠",
        "temperature": 0.9
    }
}

# Streamlit UI Config
st.set_page_config(
    page_title="AstraCode Pro",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Theme with advanced styling
def inject_custom_css(theme="Neon"):
    theme_properties = {
        "Neon": {
            "primary": "#4fffb0",
            "secondary": "#ff4fd8",
            "bg": "#1a1a2e",
            "text": "#ffffff",
            "accent": "#00ff88",
            "gradient": "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)"
        },
        "Cyberpunk": {
            "primary": "#ff2a6d",
            "secondary": "#05d9e8",
            "bg": "#1a1a2e",
            "text": "#d1f7ff",
            "accent": "#ff9a00",
            "gradient": "linear-gradient(135deg, #1a1a2e 0%, #0d1b2a 100%)"
        },
        "Solarized": {
            "primary": "#268bd2",
            "secondary": "#d33682",
            "bg": "#fdf6e3",
            "text": "#073642",
            "accent": "#cb4b16",
            "gradient": "linear-gradient(135deg, #fdf6e3 0%, #eee8d5 100%)"
        },
        "Dracula": {
            "primary": "#bd93f9",
            "secondary": "#ff79c6",
            "bg": "#282a36",
            "text": "#f8f8f2",
            "accent": "#50fa7b",
            "gradient": "linear-gradient(135deg, #282a36 0%, #44475a 100%)"
        },
        "Monokai": {
            "primary": "#a6e22e",
            "secondary": "#fd971f",
            "bg": "#272822",
            "text": "#f8f8f2",
            "accent": "#f92672",
            "gradient": "linear-gradient(135deg, #272822 0%, #1e1f1c 100%)"
        },
        "Nord": {
            "primary": "#81a1c1",
            "secondary": "#d08770",
            "bg": "#2e3440",
            "text": "#d8dee9",
            "accent": "#5e81ac",
            "gradient": "linear-gradient(135deg, #2e3440 0%, #3b4252 100%)"
        },
        "Ocean": {
            "primary": "#7fdbff",
            "secondary": "#ff851b",
            "bg": "#001f3f",
            "text": "#ffffff",
            "accent": "#2ecc40",
            "gradient": "linear-gradient(135deg, #001f3f 0%, #0074d9 100%)"
        },
        "Matrix": {
            "primary": "#00ff41",
            "secondary": "#008f11",
            "bg": "#000000",
            "text": "#00ff41",
            "accent": "#00ff41",
            "gradient": "linear-gradient(135deg, #000000 0%, #003b00 100%)"
        }
    }
    
    colors = theme_properties.get(theme, theme_properties["Neon"])
    
    st.markdown(f"""
    <style>
        /* Base styles */
        .main {{
            background: {colors['gradient']} !important;
            color: {colors['text']} !important;
        }}
        
        /* Input fields */
        .stTextInput input, .stSelectbox select, .stTextArea textarea {{
            color: {colors['primary']} !important;
            background: rgba(0,0,0,0.2) !important;
            border-radius: 12px !important;
            border: 1px solid {colors['secondary']} !important;
            padding: 10px 15px !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
            transition: all 0.3s ease !important;
        }}
        
        .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {{
            border-color: {colors['accent']} !important;
            box-shadow: 0 0 0 2px {colors['accent']}33 !important;
        }}
        
        /* Buttons */
        .stButton>button {{
            background: rgba(0,0,0,0.3) !important;
            border: 2px solid {colors['primary']} !important;
            color: {colors['primary']} !important;
            border-radius: 12px !important;
            padding: 8px 16px !important;
            transition: all 0.3s ease !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }}
        
        .stButton>button:hover {{
            background: {colors['primary']}22 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px {colors['primary']}33 !important;
        }}
        
        /* Code blocks */
        .code-block {{
            border: 2px solid {colors['secondary']};
            border-radius: 15px;
            padding: 1rem;
            background: rgba(0,0,0,0.3);
            margin-bottom: 1rem;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }}
        
        /* Sidebar */
        .sidebar .sidebar-content {{
            background: rgba(0,0,0,0.3) !important;
            backdrop-filter: blur(10px) !important;
            border-right: 1px solid {colors['secondary']}33 !important;
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: {colors['primary']} !important;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        
        /* Expander */
        .st-expander {{
            background: rgba(0,0,0,0.2) !important;
            border: 1px solid {colors['secondary']} !important;
            border-radius: 12px !important;
        }}
        
        .st-expander .st-expanderHeader {{
            color: {colors['primary']} !important;
            font-weight: 600 !important;
        }}
        
        /* Progress bar */
        .stProgress > div > div > div {{
            background: {colors['accent']} !important;
        }}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: rgba(0,0,0,0.1);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {colors['secondary']};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {colors['primary']};
        }}
        
        /* Custom cards */
        .custom-card {{
            background: rgba(0,0,0,0.2) !important;
            border-radius: 16px !important;
            padding: 20px !important;
            border: 1px solid {colors['secondary']}33 !important;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1) !important;
            margin-bottom: 20px !important;
        }}
        
        /* Tooltips */
        .stTooltip {{
            background: {colors['bg']} !important;
            color: {colors['text']} !important;
            border: 1px solid {colors['secondary']} !important;
            border-radius: 8px !important;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: rgba(0,0,0,0.2) !important;
            border-radius: 12px !important;
            padding: 8px 16px !important;
            transition: all 0.3s ease !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {colors['primary']}22 !important;
            color: {colors['primary']} !important;
            font-weight: 600 !important;
            border: 1px solid {colors['primary']} !important;
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

# Enhanced Code Generation Function
def generate_code(
    query: str, 
    language: str, 
    model: str, 
    client: Groq, 
    complexity: str,
    keywords: Optional[list] = None,
    style: Optional[str] = None
) -> Optional[str]:
    complexity_config = COMPLEXITY_LEVELS.get(complexity, COMPLEXITY_LEVELS["Medium"])
    
    prompt = f"""
    {complexity_config['description']} in {language}:
    {query}
    
    Requirements:
    - Use {language} best practices
    - Include appropriate comments
    - Follow clean code principles
    """
    
    if keywords:
        prompt += f"\nKeywords to consider: {', '.join(keywords)}"
    if style:
        prompt += f"\nCoding style: {style}"
    
    if complexity == "Expert":
        prompt += """
        Additional requirements:
        - Include performance benchmarks if applicable
        - Add scalability considerations
        - Document trade-offs and alternatives
        - Include unit tests
        """
    
    prompt += """
    IMPORTANT: Return ONLY the raw executable code with comments, 
    without any additional explanation before or after the code block.
    """
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=complexity_config['temperature'],
            max_tokens=4096,
            top_p=0.95
        )
        
        # Extract just the code block if it's wrapped in markdown
        raw_content = completion.choices[0].message.content
        if '```' in raw_content:
            code = raw_content.split('```')[1]
            if code.startswith(language.lower()):
                code = code[len(language.lower()):]
            return code.strip()
        return raw_content.strip()
    except Exception as e:
        st.error(f"Error generating code: {str(e)}")
        return None

# Code Explanation Function
def generate_explanation(code: str, language: str, client: Groq, complexity: str) -> Optional[str]:
    complexity_config = COMPLEXITY_LEVELS.get(complexity, COMPLEXITY_LEVELS["Medium"])
    
    try:
        explanation = client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=[{
                "role": "user",
                "content": f"""
                Explain this {language} code in {complexity.lower()} terms:
                {code}
                
                Structure your explanation:
                1. Overview of what the code does
                2. Key components/functions
                3. Flow of execution
                4. {complexity_config['description']} considerations
                """
            }],
            temperature=0.3,
            max_tokens=1024
        )
        return explanation.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating explanation: {str(e)}")
        return None

# Code Optimization Function
def optimize_code(code: str, language: str, client: Groq) -> Optional[str]:
    try:
        optimized = client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=[{
                "role": "user",
                "content": f"""
                Optimize this {language} code for performance and readability:
                {code}
                
                Return:
                1. Optimized code with comments explaining changes
                2. Performance benchmarks if applicable
                3. Memory usage considerations
                
                IMPORTANT: Return ONLY the raw executable code with comments, 
                without any additional explanation before or after the code block.
                """
            }],
            temperature=0.5,
            max_tokens=4096
        )
        
        raw_content = optimized.choices[0].message.content
        if '```' in raw_content:
            optimized_code = raw_content.split('```')[1]
            if optimized_code.startswith(language.lower()):
                optimized_code = optimized_code[len(language.lower()):]
            return optimized_code.strip()
        return raw_content.strip()
    except Exception as e:
        st.error(f"Error optimizing code: {str(e)}")
        return None

# Main App Interface
def main():
    client = get_groq_client()
    if not client:
        return

    # Sidebar for settings
    with st.sidebar:
        st.title("⚙️ AstraCode Pro Settings")
        
        # Theme selection with preview
        selected_theme = st.selectbox("Theme", THEMES, index=0, key="theme_select")
        inject_custom_css(selected_theme)
        
        # Language selection
        selected_language = st.selectbox("Programming Language", LANGUAGES, index=0)
        
        # Complexity selection with icons and descriptions
        complexity = st.selectbox(
            "Code Complexity",
            options=list(COMPLEXITY_LEVELS.keys()),
            format_func=lambda x: f"{COMPLEXITY_LEVELS[x]['icon']} {x}",
            index=1,
            help="Select the level of complexity for the generated code"
        )
        
        # Display complexity description
        with st.expander("Complexity Details", expanded=False):
            st.markdown(f"**{complexity}** {COMPLEXITY_LEVELS[complexity]['icon']}")
            st.caption(COMPLEXITY_LEVELS[complexity]['description'])
        
        # Additional options
        with st.expander("Advanced Options", expanded=False):
            coding_style = st.selectbox(
                "Coding Style",
                ["Default", "Functional", "OOP", "Procedural", "Concise", "Verbose"],
                index=0
            )
            
            tags = st_tags(
                label="Keywords/Tags:",
                text="Press enter to add more",
                value=[],
                key="tags",
                suggestions=["algorithm", "data structure", "API", "GUI", "CLI"]
            )
            
            auto_explain = st.checkbox("Auto-generate explanation", value=True)
            show_metadata = st.checkbox("Show code metadata", value=False)
        
        st.markdown("---")
        st.markdown("### About AstraCode Pro")
        st.caption("A next-gen AI code generator with advanced customization and theming")
    
    # Main content area
    st.title(f"💻 AstraCode Pro")
    st.caption("Generate production-ready code with AI-powered assistance")
    
    # Layout columns
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Code description input
        with st.container(border=True):
            query = st.text_area(
                "Describe your coding requirement:",
                height=150,
                placeholder="e.g., A REST API endpoint for user authentication with JWT tokens\nor\nA React component for a responsive product carousel",
                help="Be as specific as possible for better results"
            )
    
    # Initialize session state
    if 'generated_code' not in st.session_state:
        st.session_state.generated_code = None
    if 'alternative_code' not in st.session_state:
        st.session_state.alternative_code = None
    if 'optimized_code' not in st.session_state:
        st.session_state.optimized_code = None
    if 'explanation' not in st.session_state:
        st.session_state.explanation = None
    
    # Action buttons
    action_cols = st.columns([1, 1, 1, 1, 1, 2])
    
    with action_cols[0]:
        if st.button("🚀 Generate", use_container_width=True, help="Generate initial code implementation"):
            if not query:
                st.warning("Please enter a code description")
            else:
                with st.spinner(f"Generating {complexity.lower()} {selected_language} code..."):
                    progress_bar = st.progress(0)
                    
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    
                    code = generate_code(
                        query,
                        selected_language,
                        PRIMARY_MODEL,
                        client,
                        complexity,
                        tags,
                        coding_style if coding_style != "Default" else None
                    )
                    
                    if not code:
                        st.warning("Trying backup model...")
                        code = generate_code(
                            query,
                            selected_language,
                            BACKUP_MODEL,
                            client,
                            complexity,
                            tags,
                            coding_style if coding_style != "Default" else None
                        )
                    
                    if code:
                        st.session_state.generated_code = code
                        st.session_state.alternative_code = None
                        st.session_state.optimized_code = None
                        
                        if auto_explain:
                            with st.spinner("Generating explanation..."):
                                st.session_state.explanation = generate_explanation(
                                    code,
                                    selected_language,
                                    client,
                                    complexity
                                )
                    
                    progress_bar.empty()
    
    with action_cols[1]:
        if st.button("🔄 Alternative", use_container_width=True, 
                    disabled=not st.session_state.generated_code,
                    help="Generate alternative implementation"):
            with st.spinner(f"Generating alternative {selected_language} solution..."):
                alt_code = generate_code(
                    f"Alternative approach for: {query}",
                    selected_language,
                    PRIMARY_MODEL,
                    client,
                    complexity,
                    tags,
                    coding_style if coding_style != "Default" else None
                )
                if alt_code:
                    st.session_state.alternative_code = alt_code
    
    with action_cols[2]:
        if st.button("⚡ Optimize", use_container_width=True,
                    disabled=not st.session_state.generated_code,
                    help="Optimize the generated code"):
            with st.spinner(f"Optimizing {selected_language} code..."):
                optimized = optimize_code(
                    st.session_state.generated_code,
                    selected_language,
                    client
                )
                if optimized:
                    st.session_state.optimized_code = optimized
    
    with action_cols[3]:
        if st.button("📝 Explain", use_container_width=True,
                    disabled=not st.session_state.generated_code,
                    help="Generate detailed explanation"):
            with st.spinner("Generating code explanation..."):
                st.session_state.explanation = generate_explanation(
                    st.session_state.generated_code,
                    selected_language,
                    client,
                    complexity
                )
    
    with action_cols[4]:
        if st.button("🧹 Clear", use_container_width=True,
                    help="Clear all generated content"):
            st.session_state.generated_code = None
            st.session_state.alternative_code = None
            st.session_state.optimized_code = None
            st.session_state.explanation = None
    
    # Display results in tabs
    if st.session_state.generated_code:
        tab1, tab2, tab3 = st.tabs(["Generated Code", "Optimized Code", "Explanation"])
        
        with tab1:
            st.subheader(f"Generated {selected_language} Code ({complexity})")
            
            if show_metadata:
                with st.expander("Code Metadata", expanded=False):
                    metadata_cols = st.columns(3)
                    with metadata_cols[0]:
                        st.metric("Language", selected_language)
                    with metadata_cols[1]:
                        st.metric("Complexity", complexity)
                    with metadata_cols[2]:
                        st.metric("Style", coding_style)
            
            st.code(st.session_state.generated_code, language=selected_language.lower())
            
            if st.session_state.explanation and auto_explain:
                with st.expander("Auto-generated Explanation", expanded=False):
                    st.markdown(st.session_state.explanation)
        
        with tab2:
            if st.session_state.optimized_code:
                st.subheader(f"Optimized {selected_language} Code")
                st.code(st.session_state.optimized_code, language=selected_language.lower())
            else:
                st.info("Click the 'Optimize' button to generate an optimized version")
        
        with tab3:
            if st.session_state.explanation:
                st.subheader("Code Explanation")
                st.markdown(st.session_state.explanation)
            else:
                st.info("Click the 'Explain' button to generate a code explanation")
        
        # Alternative solution section
        if st.session_state.alternative_code:
            st.markdown("---")
            with st.container(border=True):
                st.subheader(f"Alternative {selected_language} Solution")
                st.code(st.session_state.alternative_code, language=selected_language.lower())
    
    # Empty state
    elif not st.session_state.generated_code and not query:
        with st.container(border=True):
            st.subheader("Welcome to AstraCode Pro!")
            st.markdown("""
            <div style="opacity: 0.8;">
            <p>Get started by:</p>
            <ol>
                <li>Describing your coding requirement in the text area</li>
                <li>Selecting your preferred language and complexity</li>
                <li>Clicking "Generate" to create your code</li>
            </ol>
            <p>Try these examples:</p>
            <ul>
                <li><i>"A Python function to calculate Fibonacci sequence with memoization"</i></li>
                <li><i>"A React component for a responsive image gallery with lazy loading"</i></li>
                <li><i>"A REST API in Node.js with Express for user authentication"</i></li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()