# 01 - Tokenization

## What is Tokenization?

**Tokenization** is the process of breaking down text into smaller units called **tokens**. In the context of Large Language Models (LLMs), tokens are the fundamental units that the model processes. A token can be a word, part of a word, or even a character, depending on the tokenization strategy used.

### Why is Tokenization Important?

- **Model Input**: LLMs don't understand raw text; they work with numerical representations of tokens
- **Context Length**: Token limits define how much text a model can process at once (e.g., GPT-4 has context windows measured in tokens)
- **Pricing**: Many AI APIs charge based on the number of tokens processed
- **Performance**: Efficient tokenization can improve model performance and reduce costs

### Common Tokenization Methods

1. **Word-level**: Each word is a token (simple but large vocabulary)
2. **Character-level**: Each character is a token (small vocabulary but long sequences)
3. **Subword**: Balance between words and characters (used by most modern LLMs)
   - **BPE (Byte Pair Encoding)**: Used by GPT models
   - **WordPiece**: Used by BERT
   - **SentencePiece**: Used by T5 and other models

## About This Code

This implementation demonstrates tokenization using OpenAI's **tiktoken** library, which is the official tokenizer for GPT models.

### What the Code Does:

```python
import tiktoken

# Load the encoding for the GPT-4o model
encoder = tiktoken.encoding_for_model("gpt-4o")

# Example text to tokenize
text = "Hello, world! This is a test of the tokenization process."

# Encode the text into tokens
tokens = encoder.encode(text)

# Print the tokens
print("Tokens:", tokens)

# Decode the tokens back to text
decoded_text = encoder.decode(tokens)

# Print the decoded text
print("Decoded text:", decoded_text)
```

### Key Features:

1. **Encoding**: Converts text into a list of integer token IDs
2. **Decoding**: Converts token IDs back to readable text
3. **Model-Specific**: Uses the exact tokenizer for GPT-4o model

### Example Output:

```
Tokens: [9906, 11, 1917, 0, 1096, 374, 264, 1296, 315, 279, 4037, 2065, 1920, 13]
Decoded text: Hello, world! This is a test of the tokenization process.
```

### Use Cases:

- **Token Counting**: Calculate tokens before API calls to estimate costs
- **Context Management**: Ensure your text fits within model limits
- **Text Processing**: Understand how models "see" your text
- **Optimization**: Identify ways to reduce token usage

## Running the Code

```bash
python main.py
```

## Key Takeaways

- Tokenization is the bridge between human text and machine learning models
- Different models use different tokenization strategies
- Token count affects both cost and context limits
- Understanding tokenization helps optimize LLM applications
