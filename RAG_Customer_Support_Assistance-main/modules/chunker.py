from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,     #  bigger chunks
        chunk_overlap=300    #  more overlap
    )
    return splitter.split_documents(documents)