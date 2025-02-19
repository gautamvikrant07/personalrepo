import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI  # Updated import
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

class PDFProcessor:
    def __init__(self):
        self.raw_text = ""
        self.vectorstore = None
        if 'conversation' not in st.session_state:
            st.session_state.conversation = None
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

    def process_documents(self, pdf_docs, embedding_choice="OpenAI"):
        self.raw_text = self.get_pdf_text(pdf_docs)
        text_chunks = self.get_text_chunks(self.raw_text)
        self.vectorstore = self.get_vectorstore(text_chunks, embedding_choice)
        st.session_state.conversation = self.get_conversation_chain(self.vectorstore)

    def get_pdf_text(self, pdf_docs):
        text = ""
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def get_text_chunks(self, text):
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        return text_splitter.split_text(text)

    def get_vectorstore(self, text_chunks, embedding_choice):
        if embedding_choice == "OpenAI":
            embeddings = OpenAIEmbeddings()  # This is now from langchain_openai
        else:
            embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
        return FAISS.from_texts(texts=text_chunks, embedding=embeddings)

    def get_conversation_chain(self, vectorstore):
        llm = ChatOpenAI()  # This is now from langchain_openai
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
        return ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            memory=memory
        )

    def handle_userinput(self, user_question):
        if st.session_state.conversation is None:
            return "Please upload and process documents first."
        
        response = st.session_state.conversation({'question': user_question})
        st.session_state.chat_history = response['chat_history']
        return response['answer']

    def reset_session(self):
        self.raw_text = ""
        self.vectorstore = None
        st.session_state.conversation = None
        st.session_state.chat_history = []

    def run(self):
        st.subheader("PDF Chat Assistant")

        # File uploader
        uploaded_files = st.file_uploader("Upload your PDFs", accept_multiple_files=True, type="pdf")

        if uploaded_files:
            if st.button("Process Documents"):
                with st.spinner("Processing..."):
                    self.process_documents(uploaded_files)
                st.success("Documents processed successfully!")

        # Chat interface
        user_question = st.text_input("Ask a question about your documents:")
        if user_question:
            response = self.handle_userinput(user_question)
            st.write("Assistant:", response)

        # Display chat history
        with st.expander("Chat History", expanded=False):
            for i, message in enumerate(st.session_state.chat_history):
                if i % 2 == 0:
                    st.write("You:", message.content)
                else:
                    st.write("Assistant:", message.content)

        if st.button("Reset Session"):
            self.reset_session()
            st.success("Session reset successfully!")
