import streamlit as st
import os
import fitz  # PyMuPDF
import base64

st.set_page_config(layout="wide")

# Ensure the 'books' directory exists
if not os.path.exists("books"):
    os.makedirs("books")

# Function to list PDF files
def list_pdf_files():
    files = os.listdir("books")
    return [file for file in files if file.endswith(".pdf")]

# Initialize session state variables
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = {}
if 'annotations' not in st.session_state:
    st.session_state.annotations = {}
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
if 'open_book' not in st.session_state:
    st.session_state.open_book = False

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["About", "Upload PDF", "Read Books"])

if page == "About":
    st.title("About")
    st.write("This is an online library application where you can upload and read PDF books.")
    st.write("Use the sidebar to navigate between different sections of the application.")

elif page == "Upload PDF":
    st.title("Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Save the uploaded file to a directory
        with open(f"books/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File {uploaded_file.name} uploaded successfully!")

elif page == "Read Books":
    st.title("Read Books")
    
    # Add search input field
    search_query = st.sidebar.text_input("Search for a book", "")
    
    # List and filter PDF files based on search query
    pdf_files = list_pdf_files()
    if search_query:
        pdf_files = [file for file in pdf_files if search_query.lower() in file.lower()]

    if pdf_files:
        selected_pdf = st.selectbox("Select a PDF file to read", pdf_files)
        
        if selected_pdf:
            if st.button("Open Book"):
                st.session_state.open_book = True

            if st.session_state.open_book:
                pdf_path = os.path.join("books", selected_pdf)
                
                with fitz.open(pdf_path) as doc:
                    num_pages = doc.page_count
                    st.write(f"### {selected_pdf}")
                    st.write(f"Total pages: {num_pages}")

                    # Zoom slider
                    zoom = st.sidebar.slider("Zoom", 0.5, 5.0, 1.0, 0.1)
                    
                    # Bookmarking
                    if selected_pdf not in st.session_state.bookmarks:
                        st.session_state.bookmarks[selected_pdf] = []

                    if st.sidebar.button("Bookmark Page"):
                        if st.session_state.page_number not in st.session_state.bookmarks[selected_pdf]:
                            st.session_state.bookmarks[selected_pdf].append(st.session_state.page_number)
                    
                    st.sidebar.write("### Bookmarked Pages")
                    for bookmark in st.session_state.bookmarks[selected_pdf]:
                        if st.sidebar.button(f"Go to Page {bookmark + 1}", key=f"bookmark-{bookmark}"):
                            st.session_state.page_number = bookmark
                    
                    # Columns for page display and notation area
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Display current page with zoom
                        page = doc.load_page(st.session_state.page_number)
                        zoom_matrix = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=zoom_matrix)
                        img = pix.tobytes("png")
                        img_base64 = base64.b64encode(img).decode("utf-8")
                        
                        # HTML and CSS for decorative frame
                        frame_html = f"""
                        <style>
                        .frame {{
                            border: 5px solid #ccc;
                            padding: 10px;
                            box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
                            background-color: #f9f9f9;
                            display: inline-block;
                            text-align: center;
                        }}
                        .fixed-buttons {{
                            position: fixed;
                            bottom: 20px;
                            left: 50%;
                            transform: translateX(-50%);
                            display: flex;
                            gap: 10px;
                            z-index: 1000;
                        }}
                        </style>
                        <div class="frame">
                            <img src="data:image/png;base64,{img_base64}" alt="PDF Page" style="width: 100%;">
                        </div>
                        """
                        
                        # Display framed image
                        st.markdown(frame_html, unsafe_allow_html=True)
                        
                        st.write(f"Showing page {st.session_state.page_number + 1} of {num_pages} (Zoom: {zoom}x)")

                        # Hidden buttons for actual navigation
                        btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
                        with btn_col1:
                            if st.button("Previous Page", key='prev-button', help="Click 'Previous Page' button at bottom of screen"):
                                if st.session_state.page_number > 0:
                                    st.session_state.page_number -= 1
                        with btn_col3:
                            if st.button("Next Page", key='next-button', help="Click 'Next Page' button at bottom of screen"):
                                if st.session_state.page_number < num_pages - 1:
                                    st.session_state.page_number += 1
                        
                        # Download button for the entire PDF book
                        download_filename = f"{selected_pdf}"
                        download_button = st.download_button(
                            label="Download Entire Book",
                            data=open(pdf_path, "rb").read(),
                            file_name=download_filename,
                            mime="application/pdf"
                        )
                    
                    with col2:
                        # Annotations
                        if selected_pdf not in st.session_state.annotations:
                            st.session_state.annotations[selected_pdf] = {}

                        annotation_text = st.text_area("Add Note/Annotation", value=st.session_state.annotations[selected_pdf].get(st.session_state.page_number, ""))
                        if st.button("Save Annotation"):
                            st.session_state.annotations[selected_pdf][st.session_state.page_number] = annotation_text
                        
                        st.write("### Notes/Annotations")
                        st.write(st.session_state.annotations[selected_pdf].get(st.session_state.page_number, "No annotations for this page."))
                        
                        st.write("### All Annotations")
                        all_annotations = st.session_state.annotations[selected_pdf]
                        for page, annotation in all_annotations.items():
                            st.write(f"Page {page + 1}: {annotation}")
                
                # Add a Close Book button
                if st.button("Close Book"):
                    st.session_state.open_book = False
                    st.session_state.page_number = 0
            else:
                st.write("Select a book and click 'Open Book' to start reading.")
    else:
        st.write("No books available.")
