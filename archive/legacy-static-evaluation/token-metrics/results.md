'''
litellm --config .\config.yaml --port 4000
←[32mINFO←[0m:     Started server process [←[36m%d←[0m]
←[32mINFO←[0m:     Waiting for application startup.

   ██╗     ██╗████████╗███████╗██╗     ██╗     ███╗   ███╗
   ██║     ██║╚══██╔══╝██╔════╝██║     ██║     ████╗ ████║
   ██║     ██║   ██║   █████╗  ██║     ██║     ██╔████╔██║
   ██║     ██║   ██║   ██╔══╝  ██║     ██║     ██║╚██╔╝██║
   ███████╗██║   ██║   ███████╗███████╗███████╗██║ ╚═╝ ██║
   ╚══════╝╚═╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝


←[1;37m#------------------------------------------------------------#←[0m
←[1;37m#                                                            #←[0m
←[1;37m#           'I get frustrated when the product...'            #←[0m
←[1;37m#        https://github.com/BerriAI/litellm/issues/new        #←[0m
←[1;37m#                                                            #←[0m
←[1;37m#------------------------------------------------------------#←[0m

 Thank you for using LiteLLM! - Krrish & Ishaan



←[1;31mGive Feedback / Get Help: https://github.com/BerriAI/litellm/issues/new←[0m


←[32mLiteLLM: Proxy initialized with Config, Set models:←[0m
←[32m    gpt-5.4←[0m
←[92m10:58:34 - LiteLLM:WARNING←[0m: utils.py:2898 - register_model: model=e6b65f9cdf0f8162e65ca2f7db116096ed823e3428e61d50e39da40ca3e071f0 not in built-in cost map and no prefix/region variant matched; cache cost fields will default to 0. To track cache cost, add cache_creation_input_token_cost and cache_read_input_token_cost to model_info
←[32mINFO←[0m:     Application startup complete.
←[32mINFO←[0m:     Uvicorn running on ←[1m%s://%s:%d←[0m (Press CTRL+C to quit)
←[92m10:58:55 - LiteLLM Proxy:ERROR←[0m: common_request_processing.py:1041 - litellm.proxy.proxy_server._handle_llm_api_exception(): Exception occured - litellm.NotFoundError: AzureException NotFoundError - Resource not found. Received Model Group=gpt-5.4
Available Model Group Fallbacks=None
Traceback (most recent call last):
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\main.py", line 640, in acompletion
    response = await _resolve_dispatched_chat_response(init_response)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\main.py", line 705, in _resolve_dispatched_chat_response
    return await pending
           ^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\llms\azure\azure.py", line 492, in acompletion
    raise e
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\llms\azure\azure.py", line 435, in acompletion
    headers, response = await self.make_azure_openai_chat_completion_request(
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\litellm_core_utils\logging_utils.py", line 289, in async_wrapper
    result: Final = await func(*args, **kwargs)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\llms\azure\azure.py", line 192, in make_azure_openai_chat_completion_request
    raise e
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\llms\azure\azure.py", line 177, in make_azure_openai_chat_completion_request
    raw_response: Final = await azure_client.chat.completions.with_raw_response.create(**data, timeout=timeout)
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\openai\_legacy_response.py", line 386, in wrapped
    return cast(LegacyAPIResponse[R], await func(*args, **kwargs))
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\openai\resources\chat\completions\completions.py", line 2907, in create
    return await self._post(
           ^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\openai\_base_client.py", line 1992, in post
    return await self.request(cast_to, opts, stream=stream, stream_cls=stream_cls)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\openai\_base_client.py", line 1777, in request
    raise self._make_status_error_from_response(err.response) from None
openai.NotFoundError: Error code: 404 - {'error': {'code': '404', 'message': 'Resource not found'}}

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\proxy\proxy_server.py", line 9875, in chat_completion
    result: Final = await base_llm_response_processor.base_process_llm_request(
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\proxy\common_request_processing.py", line 1911, in base_process_llm_request
    responses = await llm_responses
                ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\router.py", line 2181, in acompletion
    raise e
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\router.py", line 2157, in acompletion
    response = await self.async_function_with_fallbacks(**kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\router.py", line 6567, in async_function_with_fallbacks
    return await self.async_function_with_fallbacks_common_utils(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\router.py", line 6529, in async_function_with_fallbacks_common_utils
    raise original_exception
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\router.py", line 6558, in async_function_with_fallbacks
    response = await self.async_function_with_retries(*args, **kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\router.py", line 6707, in async_function_with_retries
    self.should_retry_this_error(
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\router.py", line 6886, in should_retry_this_error
    raise error
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\router.py", line 6660, in async_function_with_retries
    response = await self.make_call(original_function, *args, **kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\router.py", line 6818, in make_call
    response = await response
               ^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\router.py", line 3087, in _acompletion
    raise e
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\router.py", line 3031, in _acompletion
    response = await _response
               ^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\utils.py", line 1951, in wrapper_async
    raise e
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\utils.py", line 1760, in wrapper_async
    result = await original_function(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\main.py", line 693, in acompletion
    raise exception_type(
          ^^^^^^^^^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\litellm_core_utils\exception_mapping_utils.py", line 2510, in exception_type
    raise e  # it's already mapped
    ^^^^^^^
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\litellm_core_utils\exception_mapping_utils.py", line 2443, in exception_type
    _map_azure_exception(
  File "C:\Users\carys\token-metering\.venv\Lib\site-packages\litellm\litellm_core_utils\exception_mapping_utils.py", line 1996, in _map_azure_exception
    raise NotFoundError(
litellm.exceptions.NotFoundError: litellm.NotFoundError: AzureException NotFoundError - Resource not found. Received Model Group=gpt-5.4
Available Model Group Fallbacks=None
←[32mINFO←[0m:     127.0.0.1:53483 - "←[1mPOST /v1/chat/completions HTTP/1.1←[0m" ←[31m404 Not Found←[0m

'''
