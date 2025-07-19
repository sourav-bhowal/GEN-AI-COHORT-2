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