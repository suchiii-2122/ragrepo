# from dotenv import load_dotenv
# load_dotenv()

import os, logging
from openai import AzureOpenAI
from azure.search.documents import SearchClient # type: ignore
from azure.search.documents.models import VectorizedQuery # type: ignore
from azure.core.credentials import AzureKeyCredential

# ---------------- CLIENTS ----------------
openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), # type: ignore
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

search_client = SearchClient(
    endpoint=os.getenv("SEARCH_ENDPOINT"),
    index_name=os.getenv("SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("SEARCH_ADMIN_KEY")) # type: ignore
)

# ---------------- SEARCH ----------------
class get_response:
    @staticmethod
    def search(query, top_k=5):
        print(f"\n QUERY: {query}\n")

        # Generate query embedding
        q_vector = openai_client.embeddings.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"), # type: ignore
            input=query
        ).data[0].embedding

        vector_query = VectorizedQuery(
            vector=q_vector,
            k_nearest_neighbors=top_k,
            fields="text_vector"
        )

        results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
            select=["chunk"]
        )




        # results = search_client.search(
        #     search_text=None,
        #     vector_queries=[vector_query],
        #     select=["content", "sourceType", "sourceFile", "imageUrl"]
        # )

        # for i, r in enumerate(results, start=1):
        #     print(f"[{i}] {r['sourceType']} | {r['sourceFile']}")
        #     print(r["content"][:300])

        #     if r.get("imageUrl"):
        #         print(f"🖼️ Image: {r['imageUrl']}")

        #     print("-" * 70)


        # for i, r in enumerate(results, start=1):
        #     score = r["@search.score"]

        #     print(f"[{i}] SCORE: {score:.4f}")
        #     print(f"    Source: {r['sourceType']} | {r['sourceFile']}")
        #     print(r["content"][:300])
        #     logging.info(r["content"][:300])
        #     # return r['content']

        #     if r.get("imageUrl"):
        #         print(f"     Image: {r['imageUrl']}")
        #         logging.info(f"     Image: {r['imageUrl']}")

        #     print("-" * 70)
        # return r['content']


        final_results = []

        for i, r in enumerate(results, start=1):
            result_obj = {
                "rank": i,
                "score": round(r["@search.score"], 4),
                # "sourceType": r.get("sourceType"),
                # "sourceFile": r.get("sourceFile"),
                "chunk": r.get("chunk"),
            }

            if r.get("imageUrl"):
                result_obj["imageUrl"] = r["imageUrl"]

            # Optional logging
            logging.info({
                "rank": i,
                "score": result_obj["score"],
                "preview": result_obj["chunk"][:300]
            })

            final_results.append(result_obj)

        return final_results

# final = get_response().search("how mcuh discount given for Invoice No.SIBHI-FY23-21142")
# print(final)
# ---------------- RUN ----------------
# if __name__ == "__main__":
#     search("how mcuh discount given for Invoice No.SIBHI-FY23-21142")









# from openai import AzureOpenAI
# from azure.search.documents import SearchClient
# from azure.core.credentials import AzureKeyCredential
# import uuid
# import os
# from azure.search.documents.indexes import SearchIndexClient

# client = SearchIndexClient(
#     endpoint=os.getenv("SEARCH_ENDPOINT"],
#     credential=AzureKeyCredential(os.getenv("SEARCH_ADMIN_KEY"])
# )

# search_client = SearchClient(
#     endpoint=os.getenv("SEARCH_ENDPOINT"],
#     index_name=os.getenv("SEARCH_INDEX_NAME"],
#     credential=AzureKeyCredential(os.getenv("SEARCH_ADMIN_KEY"])
# )


# def search(query):
#     q_vector = client.embeddings.create(
#         model=os.getenv("AZURE_OPENAI_DEPLOYMENT"],
#         input=query
#     ).data[0].embedding

#     results = search_client.search(
#         search_text=None,
#         vector_queries=[{
#             "vector": q_vector,
#             "k": 5,
#             "fields": "text_vector"
#         }]
#     )

#     for r in results:
#         print(f"{r['sourceType']} | {r['sourceFile']}")
#         print(r["content"][:300])



