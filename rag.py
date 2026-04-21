import os

def get_relevant_context(query: str, k: int = 4) -> str:
    """Version simplifiée - Lecture directe des fichiers"""
    
    data_path = "data/normes"
    
    if not os.path.exists(data_path):
        return ""
    
    all_content = []
    for filename in os.listdir(data_path):
        if filename.endswith('.txt'):
            filepath = os.path.join(data_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    all_content.append(f"--- {filename} ---\n{content}")
            except Exception as e:
                print(f"Erreur lecture {filename}: {e}")
    
    if not all_content:
        return ""
    
    context = "\n\n".join(all_content)
    print(f"Contexte chargé: {len(context)} caractères")
    return context

def charger_et_indexer_documents():
    """Fonction factice pour compatibilité"""
    print("Mode simplifié - Pas de base vectorielle")
    return None
    
