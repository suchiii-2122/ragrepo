import azure.functions as func
import logging,json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="rag_git")
def rag_git(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()

        user_query = req_body.get('user_query')
    except Exception as e:
        user_query = req.params.get('user_query')
        logging.error(f'fetching user details failed due to : {e}') # type: ignore
    try:
        from  query_search import get_response
        final_response = get_response()
        
    except Exception as e:
        logging.error(f'Error Importing he module due to :{e}')
    try:
        get_finalized_respose = final_response.search(user_query)
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