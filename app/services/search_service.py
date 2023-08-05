from typing import List

import numpy as np


from pydantic import parse_obj_as

from app.utils import search_video_by_clip, vectorize_text_by_clip

from app.constants import (
    FRAME_VECTORSTORE_INDEX,
    SCENE_VECTORSTORE_INDEX,
    TRANSCRIPT_VECTORSTORE_INDEX,
    CLIP_DIMENSION,
    OPENAI_EMBEDDING,
)

from app.vectorstore import PineconeVectorStore

from app.model import VectorType, VectorMetaDataType


class SearchService:
    def __init__(self):
        self.pine_vectorstore = PineconeVectorStore()

    def search_video_by_transcript(
        self, video_uid: str, org_uid: str, query: str
    ) -> List[VectorMetaDataType]:
        embed = OPENAI_EMBEDDING
        query_vector = embed.embed_documents([query])[0]

        result = self.pine_vectorstore.search_vectors(
            index_name=TRANSCRIPT_VECTORSTORE_INDEX,
            namespace=org_uid,
            filter={},
            # filter={"video_uid": video_uid},
            vector=query_vector,
            top_k=10,
            include_values=False,
            include_metadata=True,
        )

        final_vectors: List[VectorMetaDataType] = []
        for match in result["matches"]:
            final_vectors.append(parse_obj_as(VectorMetaDataType, match["metadata"]))

        return final_vectors

    def search_video(
        self, video_uid: str, org_uid: str, query: str
    ) -> List[VectorMetaDataType]:
        query_vector = vectorize_text_by_clip(text=query)

        result = self.pine_vectorstore.search_vectors(
            index_name=SCENE_VECTORSTORE_INDEX,
            namespace=org_uid,
            filter={},
            # filter={"video_uid": video_uid},
            vector=query_vector.tolist(),
            top_k=100,
            include_values=True,
            include_metadata=True,
        )

        if len(result["matches"]) == 0:
            return []

        n_scene_vectors: List[VectorType] = []
        for match in result["matches"]:
            n_scene_vectors.append(
                VectorType(
                    id=match["id"],
                    vector=match["values"],
                    metadata=parse_obj_as(VectorMetaDataType, match["metadata"]),
                )
            )

        final_vectors: List[VectorMetaDataType] = [n_scene_vectors[0].metadata]
        for scene_vector in n_scene_vectors[1:]:
            cur_vector = scene_vector.metadata
            merged = False

            for v in final_vectors:
                # if v.end - v.start > 10:  # MIGHT NEED TO BE REMOVED (TESTING)
                #     continue
                if (cur_vector.start >= v.start and cur_vector.start <= v.end) or (
                    v.end >= cur_vector.end and v.start <= cur_vector.end
                ):
                    # Merge the overlapping ranges
                    v.start = min(v.start, cur_vector.start)
                    v.end = max(v.end, cur_vector.end)

                    merged = True
                    break

            # If original_item did not overlap with any range, add it to final_result
            if not merged:
                final_vectors.append(cur_vector)

            # Stop if we have enough results
            if len(final_vectors) >= 10:
                break

        final_cosine_sims = [-1 for i in range(len(final_vectors))]
        for index, v in enumerate(final_vectors):
            start_sec, end_sec = round(v.start), round(v.end)
            frame_vectors = self.pine_vectorstore.search_vectors(
                index_name=FRAME_VECTORSTORE_INDEX,
                namespace=org_uid,
                filter={
                    "order": {"$in": [i for i in range(start_sec + 1, end_sec + 2)]}
                },
                # filter={
                #     "$and": [
                #         {"video_uid": video_uid},
                #         {
                #             "order": {
                #                 "$in": [i for i in range(start_sec + 1, end_sec + 2)]
                #             }
                #         },
                #     ]
                # },
                vector=np.zeros(CLIP_DIMENSION).tolist(),
                top_k=end_sec - start_sec + 1,
                include_values=True,
                include_metadata=False,
            )

            for v in frame_vectors["matches"]:
                final_cosine_sims[index] = max(
                    np.dot(
                        np.array(v["values"]).astype("double"),
                        query_vector.astype("double"),
                    ),
                    final_cosine_sims[index],
                )

        coss = list(zip(final_cosine_sims, final_vectors))

        list_sorted = sorted(coss, key=lambda x: x[0], reverse=True)

        _, final_vectors = map(list, zip(*list_sorted))

        # for v in final_vectors:
        #     print("start: ", v.start, "end: ", v.end)

        return final_vectors
