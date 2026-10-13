"""
community_hub/plugins/local_knowledge_base/main.py
Index selected folders, Markdown files, documentation, and notes.
Provides fast keyword and BM25-style passage retrieval for KuroCode agents.
"""

import os
import re
import math
from typing import Dict, Any, List, Optional


class KnowledgeIndexer:
    SUPPORTED_EXTS = {".md", ".markdown", ".txt", ".rst", ".adoc", ".org"}

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.documents: List[Dict[str, Any]] = []

    def build_index(self, max_files: int = 500, chunk_size: int = 1200) -> Dict[str, Any]:
        """
        Scan directory and chunk documents for search retrieval.
        """
        if not os.path.exists(self.root_dir):
            return {"success": False, "error": f"Path '{self.root_dir}' does not exist"}

        file_count = 0
        total_chunks = 0
        self.documents = []

        for root, dirs, files in os.walk(self.root_dir):
            # Ignore hidden and virtual environment directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("venv", "node_modules", "__pycache__", "dist", "build")]

            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext in self.SUPPORTED_EXTS:
                    file_path = os.path.join(root, fname)
                    rel_path = os.path.relpath(file_path, self.root_dir)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()

                        # Break content into passage chunks
                        paragraphs = content.split("\n\n")
                        current_chunk = []
                        current_len = 0
                        chunk_idx = 0

                        for p in paragraphs:
                            p_clean = p.strip()
                            if not p_clean:
                                continue
                            if current_len + len(p_clean) > chunk_size and current_chunk:
                                chunk_text = "\n\n".join(current_chunk)
                                self.documents.append({
                                    "path": rel_path,
                                    "chunk_id": chunk_idx,
                                    "text": chunk_text,
                                    "tokens": self._tokenize(chunk_text)
                                })
                                chunk_idx += 1
                                total_chunks += 1
                                current_chunk = [p_clean]
                                current_len = len(p_clean)
                            else:
                                current_chunk.append(p_clean)
                                current_len += len(p_clean)

                        if current_chunk:
                            chunk_text = "\n\n".join(current_chunk)
                            self.documents.append({
                                "path": rel_path,
                                "chunk_id": chunk_idx,
                                "text": chunk_text,
                                "tokens": self._tokenize(chunk_text)
                            })
                            total_chunks += 1

                        file_count += 1
                        if file_count >= max_files:
                            break
                    except Exception:
                        continue

            if file_count >= max_files:
                break

        return {
            "success": True,
            "root_dir": self.root_dir,
            "indexed_files": file_count,
            "total_passages": total_chunks
        }

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9_]{2,}\b", text)]

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Score passages based on term frequency and query coverage.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scored = []
        for doc in self.documents:
            doc_tokens = set(doc["tokens"])
            token_list = doc["tokens"]
            doc_len = len(token_list) or 1

            score = 0.0
            matched_terms = []

            for q in query_tokens:
                count = token_list.count(q)
                if count > 0:
                    tf = count / doc_len
                    score += (tf * 100.0) + 1.0  # Base match bonus + TF weight
                    matched_terms.append(q)

            if score > 0:
                scored.append({
                    "score": round(score, 3),
                    "path": doc["path"],
                    "chunk_id": doc["chunk_id"],
                    "matched_terms": matched_terms,
                    "snippet": doc["text"][:350] + ("..." if len(doc["text"]) > 350 else "")
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


# Module-level instance cache for fast repeated queries
_CACHE: Dict[str, KnowledgeIndexer] = {}


def index_knowledge(directory: str = ".", max_files: int = 300) -> Dict[str, Any]:
    """
    Index documentation and notes in target directory.
    """
    abs_path = os.path.abspath(directory)
    indexer = KnowledgeIndexer(abs_path)
    res = indexer.build_index(max_files=max_files)
    if res.get("success"):
        _CACHE[abs_path] = indexer
    return res


def search_knowledge(directory: str = ".", query: str = "", top_k: int = 5) -> Dict[str, Any]:
    """
    Search indexed knowledge base passages matching query terms.
    """
    if not query.strip():
        return {"success": False, "error": "Query cannot be empty"}

    abs_path = os.path.abspath(directory)
    if abs_path not in _CACHE:
        index_res = index_knowledge(directory=abs_path)
        if not index_res.get("success"):
            return index_res

    indexer = _CACHE[abs_path]
    results = indexer.search(query=query, top_k=top_k)

    return {
        "success": True,
        "query": query,
        "directory": abs_path,
        "results_count": len(results),
        "results": results
    }
