import tiktoken
from modules.logging_utils import logger

class ConversationHandler:
    """Manages conversation state, tracks token usage, and resets when limits are reached."""
    
    def __init__(self, system_prompt, max_token_limit=8192):
        self.system_prompt = system_prompt  # ✅ System prompt (decision tree logic)
        self.history = []  # ✅ Stores messages (user + AI)
        self.max_token_limit = max_token_limit  # ✅ Model's context limit
        self.tokenizer = tiktoken.encoding_for_model("gpt-4-turbo")
        
        # ✅ Track system prompt tokens separately
        self.system_prompt_tokens = self.count_tokens(system_prompt)
        self.token_count = self.system_prompt_tokens  # ✅ Start with system tokens

    def count_tokens(self, text):
        """Uses OpenAI tokenizer to count tokens accurately."""
        return len(self.tokenizer.encode(text))

    def add_to_history(self, role, message):
        """Adds a message to conversation history and updates token count."""
        self.history.append({"role": role, "content": message})
        self.token_count += self.count_tokens(message)

    def get_full_prompt(self):
        """Resets conversation if token limit is exceeded, else returns full conversation."""
        if self.token_count > self.max_token_limit:
            logger.info("⚠️ Token limit exceeded, resetting conversation state.")
            self.reset_conversation()
        
        return [{"role": "system", "content": self.system_prompt}] + self.history

    def reset_conversation(self):
        """Clears conversation history but keeps system prompt tokens counted."""
        self.history = []
        self.token_count = self.system_prompt_tokens  # ✅ Reset but keep system tokens tracked