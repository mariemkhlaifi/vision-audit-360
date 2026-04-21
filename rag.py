import os
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

DATA_PATH  = "data/normes"
FAISS_PATH = "faiss_db"

def _get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def charger_et_indexer_documents():
    """Charge les .txt depuis DATA_PATH et crée l'index FAISS."""
    loader = DirectoryLoader(
        DATA_PATH,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    print(f"📄 {len(documents)} documents chargés depuis {DATA_PATH}")

    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=800, chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✂️  {len(chunks)} morceaux créés")

    embeddings = _get_embeddings()

    # Recrée l'index proprement
    if os.path.exists(FAISS_PATH):
        shutil.rmtree(FAISS_PATH)

    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(FAISS_PATH)
    print(f"✅ Base FAISS créée avec succès ({len(chunks)} chunks) → {FAISS_PATH}/")
    return db


def get_relevant_context(query: str, k: int = 4) -> str:
    """Utilisée par audit_engine.py — retourne les passages ISO les plus pertinents."""
    if not os.path.exists(FAISS_PATH):
        print("⚠️  Index FAISS absent. Lance d'abord : python rag.py")
        return "Aucun contexte normatif disponible."

    embeddings = _get_embeddings()
    db = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    docs = db.similarity_search(query, k=k)
    context = "\n\n".join([doc.page_content for doc in docs])
    print(f"🔍 {len(docs)} chunks récupérés pour la requête")
    return context


# Exécution une seule fois pour construire l'index
if __name__ == "__main__":
    charger_et_indexer_documents()
    