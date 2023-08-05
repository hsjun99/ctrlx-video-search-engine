import pinecone
from typing import List
from langchain.vectorstores import Pinecone

from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.docstore.document import Document


from uuid import uuid4


from app.constants import OPENAI_EMBEDDING

from app.constants import PINECONE_API_KEY, PINECONE_ENV, PINECONE_INSERT_BATCH_SIZE

from app.model import VectorType, VectorMetaDataType


class PineconeVectorStore:
    def __init__(self):
        self.batch_size = PINECONE_INSERT_BATCH_SIZE

        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

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

    def insert_vectors_from_texts(
        self,
        texts: List[str],
        metadatas: List[dict],
        index_name: str,
        namespace: str,
    ):
        index = pinecone.Index(index_name=index_name)

        embed = OPENAI_EMBEDDING

        vectors = embed.embed_documents(texts)

        upload_data = [(uuid4().hex, v, metadatas[i]) for i, v in enumerate(vectors)]

        index.upsert(
            vectors=upload_data, namespace=namespace, batch_size=self.batch_size
        )

        # return docsearch

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
        for i in range(0, len(vectors), self.batch_size):
            vectors_batch = vectors[i : i + self.batch_size]

            vectors_batch = [vector.dict() for vector in vectors_batch]

            # deleting the None values from the metadata
            for v in vectors_batch:
                v["metadata"] = {
                    k: v for k, v in v["metadata"].items() if v is not None
                }

            upload_data = [(v["id"], v["vector"], v["metadata"]) for v in vectors_batch]

            index = pinecone.Index(index_name=index_name)
            index.upsert(vectors=upload_data, namespace=namespace)

    def search_vectors(
        self,
        index_name: str,
        namespace: str,
        filter: dict,
        vector: List[float],
        top_k: int,
        include_values: bool = False,
        include_metadata: bool = False,
    ):
        index = pinecone.Index(index_name=index_name)

        ret = index.query(
            namespace=namespace,
            filter=filter,
            vector=vector,
            top_k=top_k,
            include_values=include_values,
            include_metadata=include_metadata,
        )

        return ret

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
