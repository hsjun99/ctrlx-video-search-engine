import pinecone
from typing import List
from langchain.vectorstores import Pinecone

from app.constants import OPENAI_EMBEDDING

from app.model import VectorType, VectorMetaDataType


class PineconeVectorStore:
    def __init__(self):
        pass

    def get_vectors_from_texts(
        self,
        texts: List[str],
        metadatas: List[dict],
        index_name: str,
        namespace: str,
    ):
        docsearch = Pinecone.from_texts(
            texts=texts,
            embedding=OPENAI_EMBEDDING,
            metadatas=metadatas,
            index_name=index_name,
            namespace=namespace,
        )

        return docsearch

    # def get_vectors_from_index_name(
    #     self,
    #     index_name: str,
    #     namespace: str,
    # ):
    #     docsearch = Pinecone.from_existing_index(
    #         embedding=OPENAI_EMBEDDING,
    #         index_name=index_name,
    #         namespace=namespace,
    #     )

    #     return docsearch

    def insert_vectors(
        self, index_name: str, namespace: str, vectors: List[VectorType]
    ):
        vectors = [vector.dict() for vector in vectors]

        # deleting the None values from the metadata
        for v in vectors:
            v["metadata"] = {k: v for k, v in v["metadata"].items() if v is not None}

        index = pinecone.Index(index_name=index_name)
        index.upsert(vectors=vectors, namespace=namespace)

    def delete_vectors_by_namespace(
        self,
        index_name: str,
        namespace: str,
    ):
        index = pinecone.Index(index_name=index_name)
        ret = index.delete(delete_all=True, namespace=namespace)

        return ret

    def delete_vectors_by_filter(
        self,
        index_name: str,
        namespace: str,
        filter: dict,
    ):
        index = pinecone.Index(index_name=index_name)
        ret = index.delete(namespace=namespace, filter=filter)

        return ret
