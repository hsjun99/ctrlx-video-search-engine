from typing import List

import numpy as np

from pydantic import parse_obj_as

from concurrent.futures import ThreadPoolExecutor, as_completed

from app.utils import (
    search_video_by_clip,
    vectorize_text_by_clip,
    vectorize_image_by_clip,
    check_time_overlap,
)

from app.constants import (
    FRAME_VECTORSTORE_INDEX,
    SCENE_VECTORSTORE_INDEX,
    FRAME768_VECTORSTORE_INDEX,
    SCENE768_VECTORSTORE_INDEX,
    TRANSCRIPT_VECTORSTORE_INDEX,
    # CLIP_DIMENSION,
    OPENAI_EMBEDDING,
)

CLIP_DIMENSION = 768


from app.vectorstore import PineconeVectorStore

from app.model import VectorType, VectorMetaDataType

from PIL import Image


class SearchService:
    def __init__(self):
        self.pine_vectorstore = PineconeVectorStore()

    def _search_video(
        self, query_vector: np.ndarray, org_uid: str, max_length: int = 10
    ) -> List[VectorMetaDataType]:
        with ThreadPoolExecutor() as executor:
            scene_future = executor.submit(
                lambda: self.pine_vectorstore.search_vectors(
                    index_name=SCENE768_VECTORSTORE_INDEX,
                    namespace=org_uid,
                    filter={},
                    # filter={"video_uid": video_uid},
                    vector=query_vector.tolist(),
                    top_k=200,
                    include_values=True,
                    include_metadata=True,
                )
            )
            frame_future = executor.submit(
                lambda: self.pine_vectorstore.search_vectors(
                    index_name=FRAME768_VECTORSTORE_INDEX,
                    namespace=org_uid,
                    filter={},
                    vector=query_vector.tolist(),
                    top_k=10000,
                    include_values=False,
                    include_metadata=True,
                )
            )
            result_scene = scene_future.result()
            result_frame = frame_future.result()

        if len(result_scene["matches"]) == 0:
            return []

        n_scene_vectors: List[VectorType] = []
        for match in result_scene["matches"]:
            n_scene_vectors.append(
                VectorType(
                    id=match["id"],
                    vector=match["values"],
                    metadata=parse_obj_as(VectorMetaDataType, match["metadata"]),
                )
            )

        n_frame_vectors: List[VectorType] = []
        for match in result_frame["matches"]:
            n_frame_vectors.append(
                VectorType(
                    id=match["id"],
                    metadata=parse_obj_as(VectorMetaDataType, match["metadata"]),
                )
            )

        sorted_scene_vectors: List[VectorType] = []
        added_indcices = set()
        for frame_v in n_frame_vectors:
            for index, scene_v in enumerate(n_scene_vectors):
                if index in added_indcices:
                    continue
                if (
                    frame_v.metadata.order >= round(scene_v.metadata.start) + 1
                    and frame_v.metadata.order <= round(scene_v.metadata.end) + 1
                ):
                    sorted_scene_vectors.append(scene_v)
                    added_indcices.add(index)
        for index, scene_v in enumerate(n_scene_vectors):
            if index in added_indcices:
                continue
            sorted_scene_vectors.append(scene_v)

        final_vectors: List[VectorMetaDataType] = [sorted_scene_vectors[0].metadata]
        for scene_vector in sorted_scene_vectors[1:]:
            cur_vector = scene_vector.metadata
            merged = False

            for v in final_vectors:
                if v.end - v.start > max_length:  # MIGHT NEED TO BE REMOVED (TESTING)
                    continue

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
            if len(final_vectors) >= 20:
                remove_indices = []
                for i in range(len(final_vectors) - 1):
                    if i in remove_indices:
                        continue
                    for j in range(i + 1, len(final_vectors)):
                        if j in remove_indices:
                            continue
                        if check_time_overlap(
                            start1=final_vectors[i].start,
                            end1=final_vectors[i].end,
                            start2=final_vectors[j].start,
                            end2=final_vectors[j].end,
                        ):
                            remove_indices.append(j)
                final_vectors = [
                    final_vectors[i]
                    for i in range(len(final_vectors))
                    if i not in remove_indices
                ]
                if len(final_vectors) >= 8:
                    break

        def process_vector(index, v, org_uid, query_vector):
            start_sec, end_sec = round(v.start), round(v.end)
            frame_vectors = self.pine_vectorstore.search_vectors(
                index_name=FRAME768_VECTORSTORE_INDEX,
                namespace=org_uid,
                filter={
                    "order": {"$in": [i for i in range(start_sec + 1, end_sec + 2)]}
                },
                vector=query_vector.tolist(),
                top_k=end_sec - start_sec + 1,
                include_values=False,
                include_metadata=True,
            )

            dot_sim = -1
            for v in frame_vectors["matches"]:
                dot_sim = max(dot_sim, v["score"])

            return index, dot_sim

        final_dot_sims = [-1 for _ in range(len(final_vectors))]
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(process_vector, index, v, org_uid, query_vector)
                for index, v in enumerate(final_vectors)
            ]
            for future in as_completed(futures):
                index, dot_sim = future.result()

                final_dot_sims[index] = dot_sim

        coss = list(zip(final_dot_sims, final_vectors))

        list_sorted = sorted(coss, key=lambda x: x[0], reverse=True)

        _, final_vectors = map(list, zip(*list_sorted))

        return final_vectors

    def search_video_by_text(
        self, org_uid: str, query: str
    ) -> List[VectorMetaDataType]:
        query_vector = vectorize_text_by_clip(text=query)

        final_vectors = self._search_video(query_vector=query_vector, org_uid=org_uid)

        return final_vectors

    def search_video_by_image(
        self, org_uid: str, query_image: Image.Image
    ) -> List[VectorMetaDataType]:
        query_vector = vectorize_image_by_clip(image=query_image)

        final_vectors = self._search_video(query_vector=query_vector, org_uid=org_uid)

        return final_vectors

    def search_video_by_transcript(
        self, org_uid: str, query: str
    ) -> List[VectorMetaDataType]:
        embed = OPENAI_EMBEDDING
        query_vector = embed.embed_documents([query])[0]

        result = self.pine_vectorstore.search_vectors(
            index_name=TRANSCRIPT_VECTORSTORE_INDEX,
            namespace=org_uid,
            filter={},
            vector=query_vector,
            top_k=10,
            include_values=False,
            include_metadata=True,
        )

        final_vectors: List[VectorMetaDataType] = []
        for match in result["matches"]:
            final_vectors.append(parse_obj_as(VectorMetaDataType, match["metadata"]))

        return final_vectors
