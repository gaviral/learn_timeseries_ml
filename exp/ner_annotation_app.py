import streamlit as st
import json
import streamlit.components.v1 as components

# Initialize session state for annotations
if 'annotations' not in st.session_state:
    st.session_state.annotations = []

# Initialize session state for entity types
if 'entity_types' not in st.session_state:
    st.session_state.entity_types = ['SKU']

st.title("NER Annotation Tool")
st.write("Select text and assign named entities.")

# Text input
text = st.text_area("Enter Text for Annotation:", height=200)

if text:
    st.markdown("### Annotate Entities")
    st.markdown("Select a portion of the text below, and assign an entity type from the dropdown menu.")
    
    # HTML and JavaScript for text selection
    html_code = f"""
    <div id="text-container" style="border:1px solid #ccc; padding:10px; border-radius:5px;">
        {text}
    </div>
    <script>
        const textContainer = document.getElementById("text-container");
        textContainer.addEventListener("mouseup", function() {{
            const selection = window.getSelection();
            const selectedText = selection.toString();
            if (selectedText.length > 0) {{
                const range = selection.getRangeAt(0);
                const preSelectionRange = range.cloneRange();
                preSelectionRange.selectNodeContents(textContainer);
                preSelectionRange.setEnd(range.startContainer, range.startOffset);
                const start = preSelectionRange.toString().length;
                const end = start + range.toString().length;
                // Send the data back to Streamlit using a hidden iframe
                const iframe = document.createElement('iframe');
                iframe.style.display = 'none';
                iframe.src = `/callback?selected_text=${encodeURIComponent(selectedText)}&start=${start}&end=${end}`;
                document.body.appendChild(iframe);
                setTimeout(() => { document.body.removeChild(iframe) }, 1000);
            }}
        }});
    </script>
    """
    
    # Create a hidden iframe to send data back
    components.html(html_code, height=300)
    
    # Capture query parameters for selected text
    query_params = st.experimental_get_query_params()
    selected_text = query_params.get("selected_text", [None])[0]
    start_pos = query_params.get("start", [0])[0]
    end_pos = query_params.get("end", [0])[0]
    
    if selected_text and selected_text not in [annot['text'] for annot in st.session_state.annotations]:
        st.session_state.selected_text = selected_text
        st.session_state.start_pos = int(start_pos)
        st.session_state.end_pos = int(end_pos)
    
    # Display selected text if available
    if 'selected_text' in st.session_state:
        st.write(f"**Selected Text:** {st.session_state.selected_text}")
        st.write(f"**Start Position:** {st.session_state.start_pos}")
        st.write(f"**End Position:** {st.session_state.end_pos}")
        
        # Dropdown to select entity type
        entity_type = st.selectbox("Select Entity Type:", st.session_state.entity_types)
        
        # Button to save annotation
        if st.button("Save Annotation"):
            annotation = {
                "text": st.session_state.selected_text,
                "start": st.session_state.start_pos,
                "end": st.session_state.end_pos,
                "label": entity_type
            }
            st.session_state.annotations.append(annotation)
            st.success(f"Annotated: {st.session_state.selected_text} as {entity_type}")
            del st.session_state.selected_text
            del st.session_state.start_pos
            del st.session_state.end_pos
    
    # Button to add a new entity type
    if st.button("Add New Entity Type"):
        new_entity = st.text_input("Enter new entity type:")
        if new_entity:
            st.session_state.entity_types.append(new_entity)
            st.success(f"Added new entity type: {new_entity}")
    
    # Display current annotations
    st.markdown("### Current Annotations")
    for annot in st.session_state.annotations:
        st.write(f"{annot['text']} --> {annot['label']} [{annot['start']}, {annot['end']}]")
    
    # Save annotations to a JSON file
    if st.button("Save Annotations"):
        with open("annotations.json", "w") as f:
            json.dump(st.session_state.annotations, f, indent=4)
        st.success("Annotations saved to 'annotations.json'")