from redeval.evaluators.metric import Metric
from redeval.evaluators.open_ai_completion import OpenAICompletion


class FewShotExampleFaithfulness:
    """
    Class represting an example of the evaluation that could be used for few-shot prompting.
    """

    # User's question
    context: str
    # User's question
    response: str
    # Name of the evaluation function
    eval_function: str
    # Evaluation result
    eval_result: str
    # LLM's reason for evaluation
    eval_reason: str

    def __init__(
        self,
        context: str,
        response: str,
        eval_function: str,
        eval_result: str,
        eval_reason: str,
    ):
        """
        Initialize a new instance of FewShotExample.
        """
        self.context = context
        self.response = response
        self.eval_function = eval_function
        self.eval_result = eval_result
        self.eval_reason = eval_reason


class FaithfulnessFailure(Metric):
    """
    The Faithfulness class is a metric that determines if the response can be inferred purely from the context provided.
    """

    @staticmethod
    def verdict_to_int(verdict: str) -> int:
        """
        Converts the verdict to an integer score. 'yes' verdict is considered non-failure, while 'no' verdict is considered failure.
        """
        verdict = verdict.lower()
        score = 1 if verdict == "no" else 0 if verdict == "yes" else None
        return score

    @staticmethod
    def verdict_to_bool(verdict: str) -> int:
        """
        Converts the verdict to a bool score. 'yes' verdict is considered non-failure, while 'no' verdict is considered failure.
        """
        verdict = verdict.lower()
        score = True if verdict == "no" else False if verdict == "yes" else None
        return score

    @staticmethod
    def compute(faith_eval):
        """
        Computes the faithfulness metric.
        """
        is_faithfulness_failure = FaithfulnessFailure.verdict_to_bool(faith_eval["verdict"])
        explanation = faith_eval["explanation"]
        return is_faithfulness_failure, explanation


class Faithfulness:
    """
    This class determines whether the chatbot's answer hether the response can be inferred using only the information provided as context.

    Attributes:
        openAIcompletion (OpenAICompletion): Instance for interactions with OpenAI's API.
        examples (list[FewShotExampleFaithfulness]): List of few-shot examples used for evaluation.
    """

    # Pre-defined prompts for OpenAI's GPT model
    SYSTEM_MESSAGE = """
        You are an expert at evaluating whether the response can be inferred using ONLY the information provided as context.
    """

    USER_MESSAGE_TEMPLATE = """
        Let's think step by step.
        1. Consider the following:
        context: {}.
        response:{}.
        2. Determine if the response can be inferred purely from the context provided.
        3. Provide a brief explanation of what information the response contained that was not provided to it in the context, labeled as 'explanation', leading up to a verdict (Yes/No) labeled as 'verdict'.
        4. Return a JSON object in the following format: "verdict": 'verdict', "explanation": 'explanation'.

        Here's are some examples:
        {}
    """

    def __init__(self, model, open_ai_key):
        """
        Initialize the QuestionAnswerer class.
        """
        self.openAIcompletion = OpenAICompletion(model, open_ai_key)
        self.examples = self.get_few_shot_examples()

    def evaluate(self, context: str, response: str):
        """
        Evaluation for is response faithful to context
        """
        user_message = self.USER_MESSAGE_TEMPLATE.format(context, response, self.examples)
        system_message = self.SYSTEM_MESSAGE
        message = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        openai_response = self.openAIcompletion.get_completion_from_messages(message)
        openai_response_json = self.openAIcompletion.extract_json_from_response(openai_response)

        metric_result, explanation = FaithfulnessFailure.compute(openai_response_json)
        return metric_result, explanation

    @staticmethod
    def get_few_shot_examples():
        """
        Returns the few-shot examples.
        """
        # Creating instances of the FewShotExampleCcei class for each example
        example1 = FewShotExampleFaithfulness(
            context="Y Combinator is a startup accelerator launched in March 2005. It has been used to launch more than 4,000 companies",
            response="125,000",
            eval_function="is_response_faithful_to_context",
            eval_result="No",
            eval_reason="The context does not contain any information to substantiate the response.",
        )

        # Joining the string representations of the instances
        examples = "\n\n".join([str(example1)])
        return examples
