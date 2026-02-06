import azure.functions as func
import logging,json
import os, logging
from openai import AzureOpenAI
from azure.search.documents import SearchClient # type: ignore
from azure.search.documents.models import VectorizedQuery # type: ignore
from azure.core.credentials import AzureKeyCredential


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="rag_git")
def rag_git(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        user_query = req_body.get('user_query')
        logging.info(f'recieved user query : {user_query}')
    except Exception as e:
        user_query = req.params.get('user_query')
        logging.error(f'fetching user details failed due to : {e}') # type: ignore
    try:
        openai_client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), # type: ignore
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )
    except Exception as e:
        logging.error(f'openai_client : {e}')
    
    try:

        search_client = SearchClient(
            endpoint=os.getenv("SEARCH_ENDPOINT"),
            index_name=os.getenv("SEARCH_INDEX_NAME"),
            credential=AzureKeyCredential(os.getenv("SEARCH_ADMIN_KEY")) # type: ignore
    )     
    except Exception as e:
        logging.error(f'seach_client :{e}')
    try:
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
    except Exception as e:
         logging.error(f'Error due to : {e}')

        
    try:
            get_finalized_respose = search(user_query)
            return func.HttpResponse(
            json.dumps(get_finalized_respose),
             status_code=200,
             mimetype="application/json"
        )
    except Exception as e:
            logging.error(f'failed to get  response due to : {e} ')
            return func.HttpResponse(
                json.dumps(e),
                status_code=500
            )