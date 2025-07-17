import types

class OpenAIError(Exception):
    pass

class ChatCompletion:
    @staticmethod
    def create(*args, **kwargs):
        # Return a predictable dummy response
        return {
            "choices": [
                {
                    "message": {"content": "This is a stubbed OpenAI response."}
                }
            ]
        }

# Expose module-level namespace similar to real package
error = types.SimpleNamespace(OpenAIError=OpenAIError)