from dotenv import load_dotenv
import voyageai
import re
import os

import math

from collections import Counter
from typing import Callable, Optional, Any, List, Dict, Tuple, Protocol


load_dotenv()
api_key = os.getenv("VOYAGE_API_KEY")
client = voyageai.Client()


def chunk_by_char(
    text: str,
    chunk_size: int = 150,
    chunk_overlap: int = 20
) -> list[str]:
    """
    Chunks the input text into smaller pieces based on character count.

    Args:
        text (str): The input text to be chunked.
        chunk_size (int): The maximum number of characters in each chunk.
        chunk_overlap (int): The number of overlapping characters between consecutive chunks.
    Returns:
        list[str]: A list of text chunks.
    """

    chunks = []
    start_idx = 0

    while start_idx < len(text):
        end_idx = min(start_idx + chunk_size, len(text))

        chunk_text = text[start_idx:end_idx]
        chunks.append(chunk_text)

        start_idx = (
            end_idx - chunk_overlap if end_idx < len(text) else len(text)
        )

    return chunks


def chunk_by_sentence(
    text: str,
    max_sentences_per_chunk: int = 5,
    overlap_sentences: int = 1
) -> list[str]:
    """
    Chunks the input text into smaller pieces based on sentences.

    Args:
        text (str): The input text to be chunked.
        max_sentences_per_chunk (int): The maximum number of sentences in each chunk.
        overlap_sentences (int): The number of overlapping sentences between consecutive chunks.
    Returns:
        list[str]: A list of text chunks.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    start_idx = 0

    while start_idx < len(sentences):
        end_idx = min(start_idx + max_sentences_per_chunk, len(sentences))

        current_chunk = sentences[start_idx:end_idx]
        chunks.append(" ".join(current_chunk))

        start_idx += max_sentences_per_chunk - overlap_sentences

        if start_idx < 0:
            start_idx = 0

    return chunks


# Chunk by section
def chunk_by_section(document_text: str) -> list[str]:
    """
    Chunks the input text into smaller pieces based on sections.

    Args:
        document_text (str): The input text to be chunked.
    Returns:
        list[str]: A list of text chunks.
    """

    pattern = r"\n## "

    return re.split(pattern, document_text)


def generate_embedding(
    chunks: list[str] | str,
    model: str = "voyage-3-large",
    input_type: str = "query"
) -> list[float]:
    """
    Generates an embedding for the given text using the specified model.

    Args:
        chunks (list[str] | str): The list of text chunks to be embedded or a single text string.
        model (str): The name of the embedding model to use.
        input_type (str): The type of input, either "query" or "document".
    Returns:
        list[float]: The generated embedding as a list of floats.
    """
    is_list = isinstance(chunks, list)
    input = chunks if is_list else [chunks]
    result = client.embed(input, model=model, input_type=input_type)
    return result.embeddings if is_list else result.embeddings[0]


class VectorIndex:
    """
    An in-memory vector index that stores document embeddings and supports
    nearest-neighbour search using cosine or Euclidean distance.
    """

    def __init__(
        self,
        distance_metric: str = "cosine",
        embedding_fn: Optional[Callable[[str], List[float]]] = None,
    ) -> None:
        """
        Initializes the VectorIndex.

        Args:
            distance_metric (str): Distance metric to use for similarity search.
                Must be 'cosine' or 'euclidean'. Defaults to 'cosine'.
            embedding_fn (Optional[Callable[[str], List[float]]]): A callable that
                converts a text string into a vector. Required for string-based
                add_document and search calls.
        """
        self.vectors: List[List[float]] = []
        self.documents: List[Dict[str, Any]] = []
        self._vector_dim: Optional[int] = None
        if distance_metric not in ["cosine", "euclidean"]:
            raise ValueError("distance_metric must be 'cosine' or 'euclidean'")
        self._distance_metric = distance_metric
        self._embedding_fn = embedding_fn

    def add_document(self, document: Dict[str, Any]) -> None:
        """
        Embeds and stores a document in the index.

        The document's 'content' field is passed to the embedding function and
        the resulting vector is stored alongside the document metadata.

        Args:
            document (Dict[str, Any]): A dictionary that must contain a 'content'
                key with a string value. Any additional keys are stored as metadata.

        Raises:
            ValueError: If no embedding function was provided at initialisation.
            TypeError: If document is not a dict or its 'content' is not a string.
            ValueError: If the document does not contain a 'content' key.
        """
        if not self._embedding_fn:
            raise ValueError(
                "Embedding function not provided during initialization."
            )
        if not isinstance(document, dict):
            raise TypeError("Document must be a dictionary.")
        if "content" not in document:
            raise ValueError(
                "Document dictionary must contain a 'content' key."
            )

        content = document["content"]
        if not isinstance(content, str):
            raise TypeError("Document 'content' must be a string.")

        vector = self._embedding_fn(content)
        self.add_vector(vector=vector, document=document)

    def search(
        self, query: Any, k: int = 1
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches the index for the k nearest neighbours to the query.

        Args:
            query (Any): Either a query string (requires an embedding function) or
                a pre-computed vector as a list of numbers.
            k (int): Number of nearest neighbours to return. Defaults to 1.

        Returns:
            List[Tuple[Dict[str, Any], float]]: A list of (document, distance)
                pairs sorted by ascending distance.

        Raises:
            ValueError: If no embedding function is provided for a string query,
                if the query vector dimension does not match the index, or if k <= 0.
            TypeError: If query is neither a string nor a list of numbers.
        """
        if not self.vectors:
            return []

        if isinstance(query, str):
            if not self._embedding_fn:
                raise ValueError(
                    "Embedding function not provided for string query."
                )
            query_vector = self._embedding_fn(query)
        elif isinstance(query, list) and all(
            isinstance(x, (int, float)) for x in query
        ):
            query_vector = query
        else:
            raise TypeError(
                "Query must be either a string or a list of numbers."
            )

        if self._vector_dim is None:
            return []

        if len(query_vector) != self._vector_dim:
            raise ValueError(
                f"Query vector dimension mismatch. Expected {self._vector_dim}, got {len(query_vector)}"
            )

        if k <= 0:
            raise ValueError("k must be a positive integer.")

        if self._distance_metric == "cosine":
            dist_func = self._cosine_distance
        else:
            dist_func = self._euclidean_distance

        distances = []
        for i, stored_vector in enumerate(self.vectors):
            distance = dist_func(query_vector, stored_vector)
            distances.append((distance, self.documents[i]))

        distances.sort(key=lambda item: item[0])

        return [(doc, dist) for dist, doc in distances[:k]]

    def add_vector(self, vector: List[float], document: Dict[str, Any]) -> None:
        """
        Stores a pre-computed vector together with its associated document.

        Args:
            vector (List[float]): The embedding vector to store.
            document (Dict[str, Any]): A dictionary that must contain a 'content'
                key. Any additional keys are stored as metadata.

        Raises:
            TypeError: If vector is not a list of numbers or document is not a dict.
            ValueError: If the document lacks a 'content' key, or if the vector
                dimension is inconsistent with previously stored vectors.
        """
        if not isinstance(vector, list) or not all(
            isinstance(x, (int, float)) for x in vector
        ):
            raise TypeError("Vector must be a list of numbers.")
        if not isinstance(document, dict):
            raise TypeError("Document must be a dictionary.")
        if "content" not in document:
            raise ValueError(
                "Document dictionary must contain a 'content' key."
            )

        if not self.vectors:
            self._vector_dim = len(vector)
        elif len(vector) != self._vector_dim:
            raise ValueError(
                f"Inconsistent vector dimension. Expected {self._vector_dim}, got {len(vector)}"
            )

        self.vectors.append(list(vector))
        self.documents.append(document)

    def _euclidean_distance(
        self, vec1: List[float], vec2: List[float]
    ) -> float:
        """
        Computes the Euclidean distance between two vectors.

        Args:
            vec1 (List[float]): First vector.
            vec2 (List[float]): Second vector.

        Returns:
            float: The Euclidean distance between vec1 and vec2.
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same dimension")
        return math.sqrt(sum((p - q) ** 2 for p, q in zip(vec1, vec2)))

    def _dot_product(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Computes the dot product of two vectors.

        Args:
            vec1 (List[float]): First vector.
            vec2 (List[float]): Second vector.

        Returns:
            float: The dot product of vec1 and vec2.
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same dimension")
        return sum(p * q for p, q in zip(vec1, vec2))

    def _magnitude(self, vec: List[float]) -> float:
        """
        Computes the L2 norm (magnitude) of a vector.

        Args:
            vec (List[float]): The input vector.

        Returns:
            float: The magnitude of the vector.
        """
        return math.sqrt(sum(x * x for x in vec))

    def _cosine_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Computes the cosine distance between two vectors.

        Cosine distance is defined as 1 - cosine_similarity, so it ranges from
        0 (identical direction) to 2 (opposite directions).

        Args:
            vec1 (List[float]): First vector.
            vec2 (List[float]): Second vector.

        Returns:
            float: The cosine distance between vec1 and vec2.
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same dimension")

        mag1 = self._magnitude(vec1)
        mag2 = self._magnitude(vec2)

        if mag1 == 0 and mag2 == 0:
            return 0.0
        elif mag1 == 0 or mag2 == 0:
            return 1.0

        dot_prod = self._dot_product(vec1, vec2)
        cosine_similarity = dot_prod / (mag1 * mag2)
        cosine_similarity = max(-1.0, min(1.0, cosine_similarity))

        return 1.0 - cosine_similarity

    def __len__(self) -> int:
        """Returns the number of vectors stored in the index."""
        return len(self.vectors)

    def __repr__(self) -> str:
        """Returns a human-readable summary of the index state."""
        has_embed_fn = "Yes" if self._embedding_fn else "No"
        return f"VectorIndex(count={len(self)}, dim={self._vector_dim}, metric='{self._distance_metric}', has_embedding_fn='{has_embed_fn}')"


class BM25Index:
    """
    An in-memory BM25 index that supports lexical (keyword) search over a
    collection of documents using the Okapi BM25 ranking function.
    """

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        tokenizer: Optional[Callable[[str], List[str]]] = None,
    ) -> None:
        """
        Initializes the BM25Index.

        Args:
            k1 (float): Term-frequency saturation parameter. Controls how quickly
                the contribution of repeated terms saturates. Defaults to 1.5.
            b (float): Length normalization parameter. 0 disables normalization,
                1 fully normalizes by document length. Defaults to 0.75.
            tokenizer (Optional[Callable[[str], List[str]]]): A callable that
                splits a string into a list of tokens. Defaults to a simple
                lower-case word tokenizer.
        """
        self.documents: List[Dict[str, Any]] = []
        self._corpus_tokens: List[List[str]] = []
        self._doc_len: List[int] = []
        self._doc_freqs: Dict[str, int] = {}
        self._avg_doc_len: float = 0.0
        self._idf: Dict[str, float] = {}
        self._index_built: bool = False

        self.k1 = k1
        self.b = b
        self._tokenizer = tokenizer if tokenizer else self._default_tokenizer

    def _default_tokenizer(self, text: str) -> List[str]:
        """
        Tokenizes text by lowercasing and splitting on non-word characters.

        Args:
            text (str): The input text to tokenize.

        Returns:
            List[str]: A list of non-empty tokens.
        """
        text = text.lower()
        tokens = re.split(r"\W+", text)
        return [token for token in tokens if token]

    def _update_stats_add(self, doc_tokens: List[str]) -> None:
        """
        Updates document-frequency counts and document-length tracking after
        a new document is added.

        Args:
            doc_tokens (List[str]): The tokenized content of the newly added document.
        """
        self._doc_len.append(len(doc_tokens))

        seen_in_doc = set()
        for token in doc_tokens:
            if token not in seen_in_doc:
                self._doc_freqs[token] = self._doc_freqs.get(token, 0) + 1
                seen_in_doc.add(token)

        self._index_built = False

    def _calculate_idf(self) -> None:
        """
        Computes the IDF (Inverse Document Frequency) score for every term in
        the corpus using the BM25 IDF formula.
        """
        N = len(self.documents)
        self._idf = {}
        for term, freq in self._doc_freqs.items():
            idf_score = math.log(((N - freq + 0.5) / (freq + 0.5)) + 1)
            self._idf[term] = idf_score

    def _build_index(self) -> None:
        """
        Finalizes the index by computing the average document length and IDF
        scores. Called lazily before the first search if the index is stale.
        """
        if not self.documents:
            self._avg_doc_len = 0.0
            self._idf = {}
            self._index_built = True
            return

        self._avg_doc_len = sum(self._doc_len) / len(self.documents)
        self._calculate_idf()
        self._index_built = True

    def add_document(self, document: Dict[str, Any]) -> None:
        """
        Tokenizes and stores a document in the index.

        Args:
            document (Dict[str, Any]): A dictionary that must contain a 'content'
                key with a string value. Any additional keys are stored as metadata.

        Raises:
            TypeError: If document is not a dict or its 'content' is not a string.
            ValueError: If the document does not contain a 'content' key.
        """
        if not isinstance(document, dict):
            raise TypeError("Document must be a dictionary.")
        if "content" not in document:
            raise ValueError(
                "Document dictionary must contain a 'content' key."
            )

        content = document.get("content", "")
        if not isinstance(content, str):
            raise TypeError("Document 'content' must be a string.")

        doc_tokens = self._tokenizer(content)

        self.documents.append(document)
        self._corpus_tokens.append(doc_tokens)
        self._update_stats_add(doc_tokens)

    def _compute_bm25_score(
        self, query_tokens: List[str], doc_index: int
    ) -> float:
        """
        Computes the BM25 relevance score for a single document.

        Args:
            query_tokens (List[str]): The tokenized query terms.
            doc_index (int): The index of the document in the corpus.

        Returns:
            float: The BM25 score for the document with respect to the query.
        """
        score = 0.0
        doc_term_counts = Counter(self._corpus_tokens[doc_index])
        doc_length = self._doc_len[doc_index]

        for token in query_tokens:
            if token not in self._idf:
                continue

            idf = self._idf[token]
            term_freq = doc_term_counts.get(token, 0)

            numerator = idf * term_freq * (self.k1 + 1)
            denominator = term_freq + self.k1 * (
                1 - self.b + self.b * (doc_length / self._avg_doc_len)
            )
            score += numerator / (denominator + 1e-9)

        return score

    def search(
        self,
        query_text: str,
        k: int = 1,
        score_normalization_factor: float = 0.1,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches the index for the k most relevant documents to the query.

        Raw BM25 scores are normalized to a distance-like value in (0, 1] using
        the formula: exp(-score_normalization_factor * raw_score), so lower
        values indicate higher relevance (consistent with VectorIndex).

        Args:
            query_text (str): The plain-text search query.
            k (int): Number of top results to return. Defaults to 1.
            score_normalization_factor (float): Controls how steeply higher BM25
                scores are compressed. Defaults to 0.1.

        Returns:
            List[Tuple[Dict[str, Any], float]]: A list of (document, normalized_score)
                pairs sorted by ascending normalized score (best match first).

        Raises:
            TypeError: If query_text is not a string.
            ValueError: If k <= 0.
        """
        if not self.documents:
            return []

        if not isinstance(query_text, str):
            raise TypeError("Query text must be a string.")

        if k <= 0:
            raise ValueError("k must be a positive integer.")

        if not self._index_built:
            self._build_index()

        if self._avg_doc_len == 0:
            return []

        query_tokens = self._tokenizer(query_text)
        if not query_tokens:
            return []

        raw_scores = []
        for i in range(len(self.documents)):
            raw_score = self._compute_bm25_score(query_tokens, i)
            if raw_score > 1e-9:
                raw_scores.append((raw_score, self.documents[i]))

        raw_scores.sort(key=lambda item: item[0], reverse=True)

        normalized_results = []
        for raw_score, doc in raw_scores[:k]:
            normalized_score = math.exp(-score_normalization_factor * raw_score)
            normalized_results.append((doc, normalized_score))

        normalized_results.sort(key=lambda item: item[1])

        return normalized_results

    def __len__(self) -> int:
        """Returns the number of documents stored in the index."""
        return len(self.documents)

    def __repr__(self) -> str:
        """Returns a human-readable summary of the index state."""
        return f"BM25VectorStore(count={len(self)}, k1={self.k1}, b={self.b}, index_built={self._index_built})"


class SearchIndex(Protocol):
    """
    Protocol defining the interface that all search index implementations must satisfy.
    Both VectorIndex and BM25Index conform to this protocol.
    """

    def add_document(self, document: Dict[str, Any]) -> None:
        """Adds a single document to the index."""
        ...

    # Added the 'add_documents' method to avoid rate limiting errors from VoyageAI
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Adds multiple documents to the index in bulk."""
        ...

    def search(
        self, query: Any, k: int = 1
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Returns the k most relevant (document, score) pairs for the given query.
        """
        ...


class Retriever:
    """
    Aggregates one or more SearchIndex instances and merges their results using
    Reciprocal Rank Fusion (RRF) to produce a single ranked list.
    """

    def __init__(self, *indexes: SearchIndex) -> None:
        """
        Initializes the Retriever with one or more indexes.

        Args:
            *indexes (SearchIndex): One or more index instances to query.
                Supports any combination of VectorIndex and BM25Index.

        Raises:
            ValueError: If no indexes are provided.
        """
        if len(indexes) == 0:
            raise ValueError("At least one index must be provided")
        self._indexes = list(indexes)

    def add_document(self, document: Dict[str, Any]) -> None:
        """
        Adds a single document to all underlying indexes.

        Args:
            document (Dict[str, Any]): A dictionary containing at least a
                'content' key with a string value.
        """
        for index in self._indexes:
            index.add_document(document)

    # Added the 'add_documents' method to avoid rate limiting errors from VoyageAI
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Adds multiple documents to all underlying indexes in bulk.

        Args:
            documents (List[Dict[str, Any]]): A list of document dictionaries,
                each containing at least a 'content' key with a string value.
        """
        for index in self._indexes:
            index.add_documents(documents)

    def search(
        self, query_text: str, k: int = 1, k_rrf: int = 60
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Queries all indexes and merges results with Reciprocal Rank Fusion (RRF).

        Each index is queried for k*5 candidates. RRF combines the per-index
        rankings into a single score: sum(1 / (k_rrf + rank)) over all indexes
        that returned the document. Documents with higher combined scores rank first.

        Args:
            query_text (str): The plain-text search query.
            k (int): Number of final results to return. Defaults to 1.
            k_rrf (int): RRF smoothing constant. Higher values reduce the impact
                of top-ranked results. Defaults to 60.

        Returns:
            List[Tuple[Dict[str, Any], float]]: A list of (document, rrf_score)
                pairs sorted by descending RRF score (best match first).

        Raises:
            TypeError: If query_text is not a string.
            ValueError: If k <= 0 or k_rrf < 0.
        """
        if not isinstance(query_text, str):
            raise TypeError("Query text must be a string.")
        if k <= 0:
            raise ValueError("k must be a positive integer.")
        if k_rrf < 0:
            raise ValueError("k_rrf must be non-negative.")

        all_results = [
            index.search(query_text, k=k * 5) for index in self._indexes
        ]

        doc_ranks = {}
        for idx, results in enumerate(all_results):
            for rank, (doc, _) in enumerate(results):
                doc_id = id(doc)
                if doc_id not in doc_ranks:
                    doc_ranks[doc_id] = {
                        "doc_obj": doc,
                        "ranks": [float("inf")] * len(self._indexes),
                    }
                doc_ranks[doc_id]["ranks"][idx] = rank + 1

        def calc_rrf_score(ranks: List[float]) -> float:
            return sum(1.0 / (k_rrf + r) for r in ranks if r != float("inf"))

        scored_docs: List[Tuple[Dict[str, Any], float]] = [
            (ranks["doc_obj"], calc_rrf_score(ranks["ranks"]))
            for ranks in doc_ranks.values()
        ]

        filtered_docs = [
            (doc, score) for doc, score in scored_docs if score > 0
        ]
        filtered_docs.sort(key=lambda x: x[1], reverse=True)

        return filtered_docs[:k]
